# Checkin Extension

Extends Frappe HRMS Employee Checkin with GPS, Photo, and Project tracking.

## Features

- **Project Selection** - Link each check-in/out to a specific project
- **GPS Location** - Auto-capture GPS coordinates with clickable Google Maps link
- **Photo Capture** - Take photo with front or back camera
- **Standard Integration** - Works with existing Employee Checkin doctype
- **Project Hours Report** - See hours worked by project and employee

## Requirements

- ERPNext v14 or v15
- Frappe HRMS

## Installation

```bash
cd frappe-bench
bench get-app https://github.com/yourcompany/checkin_extension
bench --site yoursite install-app checkin_extension
bench migrate  # Installs custom fields
bench build --app checkin_extension
bench restart
```

## Usage

### Mobile App
Access at: `https://yoursite.com/project-checkin`

1. Login with ERPNext credentials
2. Tap "Check In" or "Check Out"
3. Select project
4. GPS auto-detected
5. Take photo (front or back camera)
6. Confirm

### ERPNext Backend
- **Employee Checkin** - View all check-ins with project, GPS, photo
- **Project Hours Report** - See hours by project/employee

## Custom Fields Added to Employee Checkin

| Field | Type | Purpose |
|-------|------|---------|
| project | Link → Project | Which project |
| latitude | Float | GPS lat |
| longitude | Float | GPS lng |
| gps_location | Data | Google Maps link |
| checkin_photo | Attach Image | Photo |

## License

MIT
