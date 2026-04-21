frappe.query_reports["Project Hours Report"] = {
    filters: [
        {
            fieldname: "report_type",
            label: __("Report Type"),
            fieldtype: "Select",
            options: "Detailed\nWeekly Summary\nMonthly Summary",
            default: "Detailed",
            reqd: 1
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_start(),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        {
            fieldname: "employee",
            label: __("Employee"),
            fieldtype: "Link",
            options: "Employee"
        },
        {
            fieldname: "project",
            label: __("Project"),
            fieldtype: "Link",
            options: "Project"
        }
    ],
    
    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (!data) return value;
        
        // Color for hours
        if (column.fieldname === "hours" || column.fieldname === "total_hours") {
            let hours = data.hours || data.total_hours || 0;
            if (hours >= 8) {
                value = `<span style="color: #10B981; font-weight: 600;">${value}</span>`;
            } else if (hours >= 4) {
                value = `<span style="color: #F59E0B; font-weight: 600;">${value}</span>`;
            } else if (hours > 0) {
                value = `<span style="color: #EF4444; font-weight: 600;">${value}</span>`;
            }
        }
        
        // Color for avg hours
        if (column.fieldname === "avg_hours") {
            let avg = data.avg_hours || 0;
            if (avg >= 8) {
                value = `<span style="color: #10B981; font-weight: 600;">${value}</span>`;
            } else if (avg >= 6) {
                value = `<span style="color: #F59E0B; font-weight: 600;">${value}</span>`;
            } else if (avg > 0) {
                value = `<span style="color: #EF4444; font-weight: 600;">${value}</span>`;
            }
        }
        
        // Style project name
        if (column.fieldname === "project_name") {
            value = `<span style="color: #6366F1; font-weight: 500;">${value}</span>`;
        }
        
        // Style employee name
        if (column.fieldname === "employee_name") {
            value = `<span style="color: #1F2937; font-weight: 500;">${value}</span>`;
        }
        
        // Style week/month
        if (column.fieldname === "week" || column.fieldname === "month") {
            value = `<span style="background: #EEF2FF; color: #4F46E5; padding: 4px 8px; border-radius: 4px; font-weight: 500;">${value}</span>`;
        }
        
        // Style check-ins count
        if (column.fieldname === "checkins" || column.fieldname === "days_worked") {
            value = `<span style="background: #F0FDF4; color: #15803D; padding: 2px 8px; border-radius: 10px; font-weight: 500;">${value}</span>`;
        }
        
        // Style date
        if (column.fieldname === "date") {
            value = `<span style="color: #6B7280; font-weight: 500;">${value}</span>`;
        }
        
        // Style check in/out times
        if (column.fieldname === "check_in") {
            value = `<span style="color: #10B981;">▶ ${value}</span>`;
        }
        if (column.fieldname === "check_out") {
            if (value && value !== "None") {
                value = `<span style="color: #EF4444;">◼ ${value}</span>`;
            }
        }
        
        return value;
    },
    
    onload: function(report) {
        // Add custom CSS for the report
        if (!document.getElementById('project-hours-report-style')) {
            const style = document.createElement('style');
            style.id = 'project-hours-report-style';
            style.innerHTML = `
                .frappe-control[data-fieldname="report_type"] .control-input {
                    font-weight: 600;
                }
                .dt-row:hover {
                    background-color: #F8FAFC !important;
                }
                .dt-cell--header {
                    background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%) !important;
                    color: white !important;
                    font-weight: 600 !important;
                }
                .dt-scrollable {
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                .dt-row:nth-child(even) {
                    background-color: #F9FAFB;
                }
            `;
            document.head.appendChild(style);
        }
    }
};
