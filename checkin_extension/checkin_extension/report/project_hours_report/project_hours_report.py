import frappe
from frappe import _
from frappe.utils import getdate, flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 180},
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
        {"label": _("Project Name"), "fieldname": "project_name", "fieldtype": "Data", "width": 200},
        {"label": _("Check-ins"), "fieldname": "checkins", "fieldtype": "Int", "width": 100},
        {"label": _("Total Hours"), "fieldname": "total_hours", "fieldtype": "Float", "precision": 2, "width": 120},
    ]


def get_data(filters):
    conditions = []
    values = {}
    
    if filters.get("from_date"):
        conditions.append("ec.time >= %(from_date)s")
        values["from_date"] = filters.get("from_date")
    
    if filters.get("to_date"):
        conditions.append("ec.time <= %(to_date)s")
        values["to_date"] = filters.get("to_date") + " 23:59:59"
    
    if filters.get("employee"):
        conditions.append("ec.employee = %(employee)s")
        values["employee"] = filters.get("employee")
    
    if filters.get("project"):
        conditions.append("ec.project = %(project)s")
        values["project"] = filters.get("project")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Get all checkins
    checkins = frappe.db.sql(f"""
        SELECT 
            ec.employee,
            e.employee_name,
            ec.project,
            p.project_name,
            ec.log_type,
            ec.time
        FROM `tabEmployee Checkin` ec
        LEFT JOIN `tabEmployee` e ON e.name = ec.employee
        LEFT JOIN `tabProject` p ON p.name = ec.project
        WHERE {where_clause}
        ORDER BY ec.employee, ec.time
    """, values, as_dict=True)
    
    # Calculate hours per project per employee
    results = {}
    current_in = {}
    
    for c in checkins:
        key = (c.employee, c.project or "")
        
        if c.log_type == "IN":
            current_in[c.employee] = {"time": c.time, "project": c.project, "project_name": c.project_name, "employee_name": c.employee_name}
        elif c.log_type == "OUT" and c.employee in current_in:
            in_data = current_in.pop(c.employee)
            if in_data["project"] == c.project:
                hours = (c.time - in_data["time"]).total_seconds() / 3600
                if key not in results:
                    results[key] = {
                        "employee": c.employee,
                        "employee_name": c.employee_name,
                        "project": c.project or "",
                        "project_name": c.project_name or "No Project",
                        "checkins": 0,
                        "total_hours": 0
                    }
                results[key]["checkins"] += 1
                results[key]["total_hours"] += flt(hours, 2)
    
    # Convert to list and round hours
    data = []
    for key, row in results.items():
        row["total_hours"] = flt(row["total_hours"], 2)
        data.append(row)
    
    # Sort by employee, project
    data.sort(key=lambda x: (x["employee_name"] or "", x["project_name"] or ""))
    
    return data
