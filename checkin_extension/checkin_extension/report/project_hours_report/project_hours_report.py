import frappe
from frappe import _
from frappe.utils import getdate, flt, get_datetime, get_first_day, get_last_day, add_days
from datetime import datetime, timedelta


def execute(filters=None):
    report_type = filters.get("report_type", "Detailed")
    
    if report_type == "Weekly Summary":
        return get_weekly_summary(filters)
    elif report_type == "Monthly Summary":
        return get_monthly_summary(filters)
    else:
        return get_detailed_report(filters)


def get_detailed_report(filters):
    columns = [
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 100},
        {"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 140},
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 100},
        {"label": _("Project Name"), "fieldname": "project_name", "fieldtype": "Data", "width": 150},
        {"label": _("Check In"), "fieldname": "check_in", "fieldtype": "Time", "width": 90},
        {"label": _("Check Out"), "fieldname": "check_out", "fieldtype": "Time", "width": 90},
        {"label": _("Hours"), "fieldname": "hours", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("GPS"), "fieldname": "gps_in", "fieldtype": "Data", "width": 80},
    ]
    
    data = get_checkin_data(filters)
    return columns, data


def get_weekly_summary(filters):
    columns = [
        {"label": _("Week"), "fieldname": "week", "fieldtype": "Data", "width": 150},
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 100},
        {"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 100},
        {"label": _("Project Name"), "fieldname": "project_name", "fieldtype": "Data", "width": 180},
        {"label": _("Total Hours"), "fieldname": "total_hours", "fieldtype": "Float", "precision": 2, "width": 100},
        {"label": _("Check-ins"), "fieldname": "checkins", "fieldtype": "Int", "width": 80},
    ]
    
    data = get_checkin_data(filters)
    
    # Group by week, employee, project
    weekly = {}
    for row in data:
        if not row.get("date"):
            continue
        date = getdate(row["date"])
        week_start = date - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6)
        week_label = f"{week_start.strftime('%d %b')} - {week_end.strftime('%d %b %Y')}"
        
        key = (week_label, row["employee"], row["project"])
        if key not in weekly:
            weekly[key] = {
                "week": week_label,
                "employee": row["employee"],
                "employee_name": row["employee_name"],
                "project": row["project"],
                "project_name": row["project_name"],
                "total_hours": 0,
                "checkins": 0
            }
        weekly[key]["total_hours"] += flt(row.get("hours", 0))
        weekly[key]["checkins"] += 1
    
    result = list(weekly.values())
    result.sort(key=lambda x: (x["week"], x["employee_name"] or "", x["project_name"] or ""), reverse=True)
    return columns, result


def get_monthly_summary(filters):
    columns = [
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 120},
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 100},
        {"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 100},
        {"label": _("Project Name"), "fieldname": "project_name", "fieldtype": "Data", "width": 180},
        {"label": _("Total Hours"), "fieldname": "total_hours", "fieldtype": "Float", "precision": 2, "width": 100},
        {"label": _("Days Worked"), "fieldname": "days_worked", "fieldtype": "Int", "width": 100},
        {"label": _("Avg Hours/Day"), "fieldname": "avg_hours", "fieldtype": "Float", "precision": 2, "width": 100},
    ]
    
    data = get_checkin_data(filters)
    
    # Group by month, employee, project
    monthly = {}
    for row in data:
        if not row.get("date"):
            continue
        date = getdate(row["date"])
        month_label = date.strftime("%B %Y")
        
        key = (month_label, row["employee"], row["project"])
        if key not in monthly:
            monthly[key] = {
                "month": month_label,
                "employee": row["employee"],
                "employee_name": row["employee_name"],
                "project": row["project"],
                "project_name": row["project_name"],
                "total_hours": 0,
                "dates": set()
            }
        monthly[key]["total_hours"] += flt(row.get("hours", 0))
        monthly[key]["dates"].add(str(row["date"]))
    
    result = []
    for key, val in monthly.items():
        days_worked = len(val["dates"])
        result.append({
            "month": val["month"],
            "employee": val["employee"],
            "employee_name": val["employee_name"],
            "project": val["project"],
            "project_name": val["project_name"],
            "total_hours": flt(val["total_hours"], 2),
            "days_worked": days_worked,
            "avg_hours": flt(val["total_hours"] / days_worked, 2) if days_worked else 0
        })
    
    result.sort(key=lambda x: (x["month"], x["employee_name"] or "", x["project_name"] or ""), reverse=True)
    return columns, result


def get_checkin_data(filters):
    conditions = []
    values = {}
    
    if filters.get("from_date"):
        conditions.append("DATE(ec_in.time) >= %(from_date)s")
        values["from_date"] = filters.get("from_date")
    
    if filters.get("to_date"):
        conditions.append("DATE(ec_in.time) <= %(to_date)s")
        values["to_date"] = filters.get("to_date")
    
    if filters.get("employee"):
        conditions.append("ec_in.employee = %(employee)s")
        values["employee"] = filters.get("employee")
    
    if filters.get("project"):
        conditions.append("ec_in.project = %(project)s")
        values["project"] = filters.get("project")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
        SELECT 
            DATE(ec_in.time) as date,
            ec_in.employee,
            e.employee_name,
            ec_in.project,
            p.project_name,
            ec_in.time as check_in,
            ec_in.gps_link as gps_in,
            (
                SELECT MIN(ec_out.time)
                FROM `tabEmployee Checkin` ec_out
                WHERE ec_out.employee = ec_in.employee
                AND IFNULL(ec_out.project, '') = IFNULL(ec_in.project, '')
                AND ec_out.log_type = 'OUT'
                AND ec_out.time > ec_in.time
                AND DATE(ec_out.time) = DATE(ec_in.time)
            ) as check_out
        FROM `tabEmployee Checkin` ec_in
        LEFT JOIN `tabEmployee` e ON e.name = ec_in.employee
        LEFT JOIN `tabProject` p ON p.name = ec_in.project
        WHERE ec_in.log_type = 'IN'
        AND {where_clause}
        ORDER BY ec_in.time DESC
    """
    
    results = frappe.db.sql(query, values, as_dict=True)
    
    data = []
    for row in results:
        hours = 0
        check_in_time = ""
        check_out_time = ""
        
        if row.check_in:
            check_in_time = get_datetime(row.check_in).strftime("%I:%M %p")
        if row.check_out:
            check_out_time = get_datetime(row.check_out).strftime("%I:%M %p")
            diff = get_datetime(row.check_out) - get_datetime(row.check_in)
            hours = flt(diff.total_seconds() / 3600, 2)
        
        gps_link = ""
        if row.gps_in:
            gps_link = f'<a href="{row.gps_in}" target="_blank">📍 Map</a>'
        
        data.append({
            "date": row.date,
            "employee": row.employee,
            "employee_name": row.employee_name,
            "project": row.project,
            "project_name": row.project_name or "No Project",
            "check_in": check_in_time,
            "check_out": check_out_time,
            "hours": hours,
            "gps_in": gps_link,
        })
    
    return data
