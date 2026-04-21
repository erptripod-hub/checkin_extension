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
    
    # Create Employee Checkin (uses HRMS existing fields + our custom fields)
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


@frappe.whitelist()
def get_project_hours_report(from_date=None, to_date=None, employee=None):
    """Get hours worked by project"""
    filters = {}
    if from_date:
        filters["time"] = [">=", from_date]
    if to_date:
        if "time" in filters:
            filters["time"] = ["between", [from_date, to_date + " 23:59:59"]]
        else:
            filters["time"] = ["<=", to_date + " 23:59:59"]
    if employee:
        filters["employee"] = employee
    
    checkins = frappe.get_all("Employee Checkin",
        filters=filters,
        fields=["employee", "log_type", "time", "project"],
        order_by="employee, time"
    )
    
    results = {}
    current_in = {}
    
    for c in checkins:
        key = (c.employee, c.project or "No Project")
        
        if c.log_type == "IN":
            current_in[c.employee] = {"time": c.time, "project": c.project}
        elif c.log_type == "OUT" and c.employee in current_in:
            in_data = current_in.pop(c.employee)
            if in_data["project"] == c.project:
                hours = (c.time - in_data["time"]).total_seconds() / 3600
                if key not in results:
                    results[key] = {"employee": c.employee, "project": c.project or "No Project", "hours": 0}
                results[key]["hours"] += hours
    
    return list(results.values())
