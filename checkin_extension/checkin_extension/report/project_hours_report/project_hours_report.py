import frappe
from frappe import _
from frappe.utils import getdate, flt, get_datetime


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 120},
        {"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 120},
        {"label": _("Project Name"), "fieldname": "project_name", "fieldtype": "Data", "width": 180},
        {"label": _("Check In"), "fieldname": "check_in", "fieldtype": "Datetime", "width": 150},
        {"label": _("Check Out"), "fieldname": "check_out", "fieldtype": "Datetime", "width": 150},
        {"label": _("Hours"), "fieldname": "hours", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("GPS In"), "fieldname": "gps_in", "fieldtype": "Data", "width": 120},
        {"label": _("GPS Out"), "fieldname": "gps_out", "fieldtype": "Data", "width": 120},
    ]


def get_data(filters):
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
    
    # Get all IN checkins with their matching OUT checkins
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
                AND ec_out.project = ec_in.project
                AND ec_out.log_type = 'OUT'
                AND ec_out.time > ec_in.time
                AND DATE(ec_out.time) = DATE(ec_in.time)
            ) as check_out,
            (
                SELECT ec_out.gps_link
                FROM `tabEmployee Checkin` ec_out
                WHERE ec_out.employee = ec_in.employee
                AND ec_out.project = ec_in.project
                AND ec_out.log_type = 'OUT'
                AND ec_out.time > ec_in.time
                AND DATE(ec_out.time) = DATE(ec_in.time)
                ORDER BY ec_out.time ASC
                LIMIT 1
            ) as gps_out
        FROM `tabEmployee Checkin` ec_in
        LEFT JOIN `tabEmployee` e ON e.name = ec_in.employee
        LEFT JOIN `tabProject` p ON p.name = ec_in.project
        WHERE ec_in.log_type = 'IN'
        AND {where_clause}
        ORDER BY ec_in.time DESC
    """
    
    results = frappe.db.sql(query, values, as_dict=True)
    
    # Calculate hours and format GPS links
    data = []
    for row in results:
        hours = 0
        if row.check_in and row.check_out:
            diff = get_datetime(row.check_out) - get_datetime(row.check_in)
            hours = flt(diff.total_seconds() / 3600, 2)
        
        # Make GPS links clickable
        gps_in = ""
        gps_out = ""
        if row.gps_in:
            gps_in = f'<a href="{row.gps_in}" target="_blank">📍 View</a>'
        if row.gps_out:
            gps_out = f'<a href="{row.gps_out}" target="_blank">📍 View</a>'
        
        data.append({
            "date": row.date,
            "employee": row.employee,
            "employee_name": row.employee_name,
            "project": row.project,
            "project_name": row.project_name or "No Project",
            "check_in": row.check_in,
            "check_out": row.check_out,
            "hours": hours,
            "gps_in": gps_in,
            "gps_out": gps_out,
        })
    
    return data
