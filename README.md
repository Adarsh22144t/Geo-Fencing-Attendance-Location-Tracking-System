# Geo-Fencing Attendance & Location Tracking System

A web-based attendance system that uses **geo-fencing** to verify whether a user is within an authorized area (office/campus) before marking attendance. It includes:

- Employee-facing **check-in page**
- Admin-only **dashboard with map**, configurable **office location & radius**
- **CSV export** of attendance logs (with automatic clearing after download)

---

## 🔍 Problem Statement Mapping (Cerevyn PS-9)

**Cerevyn Geo-Fencing Attendance & Location Tracking System**

This project implements:

- Capture user location via mobile/website  
- Compare with predefined geo-fence radius  
- Mark attendance only if user is inside boundary  
- Track movement history via logged coordinates and timestamps  
- Admin dashboard for location logs and configuration  

---

## ✨ Features

### 👤 Employee Features

- Web page to:
  - Enter **Employee ID** and **Name**
  - Click **“Mark Attendance”**
- Uses browser **Geolocation API** to capture live latitude & longitude
- Checks if user is **inside defined geo-fence**
- Shows clear result:
  - ✅ INSIDE GEOFENCE (Present)
  - ❌ OUTSIDE GEOFENCE
- Displays **live location coordinates** on the page

---

### 🛡 Admin Features

- **Admin login** (username/password)
- **Admin Dashboard**:
  - View all recent attendance records in a table:
    - Employee ID
    - Name
    - Status (Present / Outside Geofence)
    - Distance from office (meters)
    - Latitude & Longitude
    - Timestamp
  - **Interactive map** (Leaflet + OpenStreetMap):
    - Office location marker
    - Blue circle showing geofence radius
    - Check-in markers for employees

- **Configurable office location and radius**:
  - Update **office latitude**, **longitude**, and **radius (meters)** directly from admin page
  - Changes are stored in the database and immediately used in geofence checks

- **CSV export with auto-clear logs**:
  - Button: **“Download & Clear Logs (CSV)”**
  - Downloads all current attendance logs as a CSV file
  - Automatically **deletes all records** from `attendance` table after export
  - Next download will contain only **new** records

---

## 🧱 Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, Bootstrap, JavaScript
- **Database:** SQLite
- **Maps:** Leaflet.js + OpenStreetMap
- **Location:** Browser Geolocation API (`navigator.geolocation`)

---

## 📁 Project Structure

```text
geo_attendance/
├── app.py
├── attendance.db          # auto-created at first run
├── requirements.txt
├── static/
│   └── style.css
└── templates/
    ├── index.html         # Employee page
    ├── admin.html         # Admin dashboard
    └── admin_login.html   # Admin login page
