# Geo-Fencing Attendance & Location Tracking System

A smart attendance system based on **Geo-Fencing**, designed to validate employee presence based on GPS coordinates before allowing attendance marking. This project provides a **secure, location-aware, web-based attendance solution** for offices, campuses, and field workers.

---

## 🎯 Problem Statement (Cerevyn Solutions — PS-9)

**“Geo-Fencing Attendance & Location Tracking System”**

This project fulfills all core requirements of the given problem statement:

- Capture live user location via browser/mobile  
- Validate if the user is inside a defined geofence radius  
- Record attendance logs with timestamp, location, and status  
- Admin dashboard with map visualization  
- Auto log download and clean-up  
- Flexible location management by admin  

---

## 📌 Key Features

### 👨‍💼 Employee Portal
- Simple UI to enter Employee ID and Name  
- Captures **live location via browser**  
- Marks attendance only if within geofence radius  
- Clear result shown:  
  - `✔ INSIDE GEOFENCE` (Present)  
  - `❌ OUTSIDE GEOFENCE` (Not allowed)  
- Displays **live GPS coordinates**  
- Fully web-based — no app required  

---

### 🔐 Admin Portal

| Feature                    | Description                                      |
|---------------------------|--------------------------------------------------|
| Secure Login              | Username + password (default: admin/admin123)    |
| Dashboard                 | View logs, map, and configuration                |
| Live Map                  | Office location + geofence + check-ins           |
| Update Location           | Edit office lat/lng + radius via UI              |
| CSV Export                | Download and auto-clear attendance logs          |
| Clear Logs Automatically  | Logs wiped from DB after export                  |
| Session-secured           | Admin session persists during use                |

---

## 🧱 Tech Stack

| Layer          | Tech Used                        |
|----------------|----------------------------------|
| Backend        | Python + Flask                   |
| Frontend       | HTML, Bootstrap, JavaScript      |
| Database       | SQLite                           |
| Geolocation    | `navigator.geolocation` (browser) |
| Map UI         | Leaflet.js + OpenStreetMap       |

---

## 🖼️ Demo UI Preview (Add Screenshots Here)

| Employee Page                      | Admin Dashboard                          |
|-----------------------------------|-------------------------------------------|
| Live location + attendance form   | Map + logs + location update + CSV export |

> 🚀 Add screenshots or GIFs here to make your README visually appealing on GitHub.

---

## 📥 Installation Guide

### 🔧 Prerequisites
- Python 3.8+  
- pip  
- Git (optional)  
- Virtual environment tool (recommended)

---

## 🧪 Usage Instructions

### 👤 Employee

- Open: `http://127.0.0.1:5000`
- Enter: Employee ID and Name
- Allow browser to access location
- Click “Mark Attendance”
- You will see:
  - Live GPS location
  - Attendance status: Present or Outside Geofence
  - Distance from office location

---

### 🔸 Admin

- Go to: `http://127.0.0.1:5000/admin/login`
- Login using:
  - Username: `admin`
  - Password: `admin123`
- Dashboard includes:
  - Map with geofence
  - Live check-ins
  - Editable office location & radius
  - Export logs as CSV and clear logs automatically

---

## ⚙️ Configuration

### Default Geofence Settings (in `app.py`)
```python
DEFAULT_OFFICE_LAT = 18.573441
DEFAULT_OFFICE_LNG = 83.361742
DEFAULT_RADIUS_M = 200  # meters

#Project structure
geo_attendance/
│── app.py
│── attendance.db          # Auto-created database
│── requirements.txt
│
├── static/
│   └── style.css
│
└── templates/
    ├── index.html
    ├── admin_login.html
    └── admin.html


