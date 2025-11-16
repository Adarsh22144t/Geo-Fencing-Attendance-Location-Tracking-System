from flask import Flask, render_template, request, jsonify, send_file
import math
import sqlite3
import os
import tempfile

app = Flask(__name__)

DB_PATH = "attendance.db"

# 🔵 Set your office / campus location here
OFFICE_LAT = 17.734042  # example values – change to your location if you want
OFFICE_LNG = 83.286426

# OFFICE_LAT = 17.734042  # example values – change to your location if you want
# OFFICE_LNG = 83.286426
GEOFENCE_RADIUS_M = 200  # meters


def init_db():
    """Create attendance table if not exists."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT,
            emp_name TEXT,
            lat REAL,
            lng REAL,
            distance_m REAL,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def haversine_m(lat1, lon1, lat2, lon2):
    """Distance between two lat/lng points in meters."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/mark", methods=["POST"])
def mark_attendance():
    data = request.get_json()
    emp_id = (data.get("emp_id") or "").strip()
    emp_name = (data.get("emp_name") or "").strip()
    lat = data.get("lat")
    lng = data.get("lng")

    if not emp_id or not emp_name:
        return jsonify({"ok": False, "message": "Please enter Employee ID and Name."}), 400

    if lat is None or lng is None:
        return jsonify({"ok": False, "message": "Location not received."}), 400

    try:
        lat = float(lat)
        lng = float(lng)
    except ValueError:
        return jsonify({"ok": False, "message": "Invalid coordinates."}), 400

    distance = haversine_m(lat, lng, OFFICE_LAT, OFFICE_LNG)
    inside = distance <= GEOFENCE_RADIUS_M
    status = "Present" if inside else "Outside Geofence"

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO attendance (emp_id, emp_name, lat, lng, distance_m, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (emp_id, emp_name, lat, lng, distance, status),
    )
    conn.commit()
    conn.close()

    message = (
        f"✅ Attendance marked as PRESENT. Distance: {distance:.1f} m"
        if inside
        else f"❌ You are OUTSIDE the allowed area. Distance: {distance:.1f} m"
    )

    return jsonify(
    {
        "ok": True,
        "inside": inside,
        "status": status,
        "distance_m": round(distance, 2),
        "message": message,
        "user_lat": lat,
        "user_lng": lng,
        "office_lat": OFFICE_LAT,
        "office_lng": OFFICE_LNG,
        "radius_m": GEOFENCE_RADIUS_M,
    }
)

    


@app.route("/admin")
def admin():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, emp_id, emp_name, lat, lng, distance_m, status, created_at "
        "FROM attendance ORDER BY id DESC LIMIT 100"
    )
    rows = cur.fetchall()
    conn.close()

    records = []
    for r in rows:
        records.append(
            {
                "id": r[0],
                "emp_id": r[1],
                "emp_name": r[2],
                "lat": r[3],
                "lng": r[4],
                "distance_m": r[5],
                "status": r[6],
                "created_at": r[7],
            }
        )

    return render_template(
        "admin.html",
        records=records,
        office_lat=OFFICE_LAT,
        office_lng=OFFICE_LNG,
        radius_m=GEOFENCE_RADIUS_M,
    )


@app.route("/download-logs")
def download_logs():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT emp_id, emp_name, lat, lng, distance_m, status, created_at FROM attendance ORDER BY id DESC"
    )
    rows = cur.fetchall()
    conn.close()

    lines = ["emp_id,emp_name,lat,lng,distance_m,status,created_at"]
    for r in rows:
        line = f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]},{r[5]},{r[6]}"
        lines.append(line)

    csv_data = "\n".join(lines)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    with open(tmp.name, "w", encoding="utf-8") as f:
        f.write(csv_data)

    return send_file(tmp.name, as_attachment=True, download_name="attendance_logs.csv")


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Starting Flask server...")
    app.run(debug=True)
