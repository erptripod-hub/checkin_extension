app_name = "checkin_extension"
app_title = "Checkin Extension"
app_publisher = "Your Company"
app_description = "Extends HRMS Employee Checkin with GPS, Photo and Project tracking"
app_email = "info@yourcompany.com"
app_license = "MIT"

# Required Apps
required_apps = ["frappe", "erpnext", "hrms"]

# Fixtures - Custom Fields added to Employee Checkin
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "Checkin Extension"]]
    }
]

# Include JS in Employee Checkin form (for ERPNext desktop)
doctype_js = {
    "Employee Checkin": "public/js/employee_checkin.js"
}

# Include JS everywhere (both desk and web)
app_include_js = "/assets/checkin_extension/js/hrms_inject.js"
web_include_js = "/assets/checkin_extension/js/hrms_inject.js"

# Website Route Rules
website_route_rules = [
    {"from_route": "/project-checkin", "to_route": "project-checkin"},
]
