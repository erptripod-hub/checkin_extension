import frappe
from frappe import _
from frappe.utils import nowdate, now_datetime, getdate
import base64


@frappe.whitelist()
def get_employee_info():
    """Get current user's employee info"""
    user = frappe.session.user
    emp = frappe.db.get_value("Employee", 
        {"user_id": user, "status": "Active"},
        ["name", "employee_name", "department", "designation", "company", "image"], 
        as_dict=True
    )
    if not emp:
        frappe.throw(_("No active employee found for your account"))
    return emp


@frappe.whitelist()
def get_projects():
    """Get active projects list"""
    return frappe.get_all("Project",
        filters={"status": ["not in", ["Completed", "Cancelled"]]},
        fields=["name", "project_name", "customer"],
        order_by="project_name",
        limit_page_length=0
    )


@frappe.whitelist()
def get_open_checkin():
    """Get current open check-in (IN without OUT) for today"""
    emp = get_employee_info()
    today = nowdate()
    
    # Find last IN that doesn't have a matching OUT
    last_in = frappe.db.sql("""
        SELECT ec.name, ec.project, ec.time, ec.gps_link, p.project_name
        FROM `tabEmployee Checkin` ec
        LEFT JOIN `tabProject` p ON p.name = ec.project
        WHERE ec.employee = %s
        AND ec.log_type = 'IN'
        AND DATE(ec.time) = %s
        AND NOT EXISTS (
            SELECT 1 FROM `tabEmployee Checkin` ec_out
            WHERE ec_out.employee = ec.employee
            AND ec_out.log_type = 'OUT'
            AND ec_out.project = ec.project
            AND ec_out.time > ec.time
            AND DATE(ec_out.time) = %s
        )
        ORDER BY ec.time DESC
        LIMIT 1
    """, (emp.name, today, today), as_dict=True)
    
    if last_in:
        return {
            "has_open": True,
            "checkin_name": last_in[0].name,
            "project": last_in[0].project,
            "project_name": last_in[0].project_name,
            "check_in_time": last_in[0].time,
            "gps_link": last_in[0].gps_link
        }
    
    return {"has_open": False}


@frappe.whitelist()
def get_today_entries():
    """Get today's check-in entries for current employee"""
    emp = get_employee_info()
    today = nowdate()
    
    entries = frappe.get_all("Employee Checkin",
        filters={
            "employee": emp.name,
            "time": ["between", [f"{today} 00:00:00", f"{today} 23:59:59"]]
        },
        fields=["name", "log_type", "time", "project", "gps_link", "checkin_photo", "latitude", "longitude"],
        order_by="time desc"
    )
    
    # Get project names
    for entry in entries:
        if entry.project:
            entry.project_name = frappe.db.get_value("Project", entry.project, "project_name")
    
    return entries


@frappe.whitelist()
def create_checkin(log_type, project, latitude=None, longitude=None, photo=None):
    """Create Employee Checkin with GPS and photo"""
    emp = get_employee_info()
    
    # Build Google Maps URL
    gps_link = ""
    if latitude and longitude:
        gps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
    
    # Save photo
    photo_url = None
    if photo and photo.startswith("data:"):
        photo_url = save_photo(photo, emp.name, log_type)
    
    # Create Employee Checkin
    checkin = frappe.get_doc({
        "doctype": "Employee Checkin",
        "employee": emp.name,
        "log_type": log_type,
        "time": now_datetime(),
        "project": project,
        "latitude": float(latitude) if latitude else None,
        "longitude": float(longitude) if longitude else None,
        "gps_link": gps_link,
        "checkin_photo": photo_url
    })
    checkin.insert(ignore_permissions=True)
    
    return {
        "success": True,
        "message": f"{'Checked in' if log_type == 'IN' else 'Checked out'} successfully",
        "name": checkin.name
    }


def save_photo(base64_data, employee, prefix):
    """Save base64 photo to file"""
    if not base64_data:
        return None
    try:
        content = base64_data.split(",")[1] if "," in base64_data else base64_data
        file_content = base64.b64decode(content)
        filename = f"{prefix}_{employee}_{now_datetime().strftime('%Y%m%d_%H%M%S')}.jpg"
        from frappe.utils.file_manager import save_file
        f = save_file(filename, file_content, "Employee Checkin", employee, is_private=1)
        return f.file_url
    except Exception as e:
        frappe.log_error(str(e), "Photo Save Error")
        return None
