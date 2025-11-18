from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    redirect,
    url_for,
    session,
)
import math
import sqlite3
import os
import tempfile
from functools import wraps

app = Flask(__name__)
app.secret_key = "change_this_secret_key"  # needed for sessions/login

DB_PATH = "attendance.db"

# Default office config (used only if DB has no values yet)
DEFAULT_OFFICE_LAT = 18.465364
DEFAULT_OFFICE_LNG = 83.661536
DEFAULT_RADIUS_M = 200

# Simple admin credentials (you can change these)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# ---------- DB helpers ----------

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if not exist and insert default office config."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Attendance table
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

    # Settings table for office location & radius
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )

    # Ensure default settings exist
    cur.execute("SELECT COUNT(*) as c FROM settings")
    count = cur.fetchone()["c"]
    if count == 0:
        cur.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)",
            ("office_lat", str(DEFAULT_OFFICE_LAT)),
        )
        cur.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)",
            ("office_lng", str(DEFAULT_OFFICE_LNG)),
        )
        cur.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)",
            ("radius_m", str(DEFAULT_RADIUS_M)),
        )

    conn.commit()
    conn.close()


def get_office_config():
    """Fetch office_lat, office_lng, radius_m from settings table."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT key, value FROM settings")
    rows = cur.fetchall()
    conn.close()

    cfg = {
        "office_lat": DEFAULT_OFFICE_LAT,
        "office_lng": DEFAULT_OFFICE_LNG,
        "radius_m": DEFAULT_RADIUS_M,
    }

    for row in rows:
        k = row["key"]
        v = row["value"]
        if k == "office_lat":
            cfg["office_lat"] = float(v)
        elif k == "office_lng":
            cfg["office_lng"] = float(v)
        elif k == "radius_m":
            cfg["radius_m"] = float(v)

    return cfg


def update_office_config(lat, lng, radius_m):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        ("office_lat", str(lat)),
    )
    cur.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        ("office_lng", str(lng)),
    )
    cur.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        ("radius_m", str(radius_m)),
    )
    conn.commit()
    conn.close()


# ---------- Geo helpers ----------

def haversine_m(lat1, lon1, lat2, lon2):
    """Distance between two lat/lng points in meters."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(
        d_lambda / 2
    ) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ---------- Auth helpers ----------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)

    return decorated


# ---------- Routes: User side ----------

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

    office_cfg = get_office_config()
    office_lat = office_cfg["office_lat"]
    office_lng = office_cfg["office_lng"]
    radius_m = office_cfg["radius_m"]

    distance = haversine_m(lat, lng, office_lat, office_lng)
    inside = distance <= radius_m
    status = "Present" if inside else "Outside Geofence"

    conn = get_db_connection()
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
        f"Attendance marked as PRESENT. Distance: {distance:.2f} m"
        if inside
        else f"You are OUTSIDE the allowed area. Distance: {distance:.2f} m"
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
            "office_lat": office_lat,
            "office_lng": office_lng,
            "radius_m": radius_m,
        }
    )


# ---------- Routes: Admin auth ----------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        else:
            error = "Invalid username or password."
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
@login_required
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


# ---------- Routes: Admin dashboard ----------

@app.route("/admin")
@login_required
def admin():
    office_cfg = get_office_config()
    office_lat = office_cfg["office_lat"]
    office_lng = office_cfg["office_lng"]
    radius_m = office_cfg["radius_m"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, emp_id, emp_name, lat, lng, distance_m, status, created_at "
        "FROM attendance ORDER BY id DESC LIMIT 200"
    )
    rows = cur.fetchall()
    conn.close()

    records = [dict(r) for r in rows]

    return render_template(
        "admin.html",
        records=records,
        office_lat=office_lat,
        office_lng=office_lng,
        radius_m=radius_m,
    )


@app.route("/update-location", methods=["POST"])
@login_required
def update_location_route():
    try:
        new_lat = float(request.form.get("office_lat"))
        new_lng = float(request.form.get("office_lng"))
        new_radius = float(request.form.get("radius_m"))
    except (TypeError, ValueError):
        return redirect(url_for("admin"))

    update_office_config(new_lat, new_lng, new_radius)
    return redirect(url_for("admin"))


@app.route("/download-logs")
@login_required
def download_logs():
    # Fetch all current logs
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT emp_id, emp_name, lat, lng, distance_m, status, created_at "
        "FROM attendance ORDER BY id DESC"
    )
    rows = cur.fetchall()

    # Build CSV content
    lines = ["emp_id,emp_name,lat,lng,distance_m,status,created_at"]
    for r in rows:
        line = f"{r['emp_id']},{r['emp_name']},{r['lat']},{r['lng']},{r['distance_m']},{r['status']},{r['created_at']}"
        lines.append(line)

    csv_data = "\n".join(lines)

    # Write to temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    with open(tmp.name, "w", encoding="utf-8") as f:
        f.write(csv_data)

    # ⚠️ Clear old records after export
    cur.execute("DELETE FROM attendance")
    conn.commit()
    conn.close()

    return send_file(tmp.name, as_attachment=True, download_name="attendance_logs.csv")


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Starting Flask server...")
    app.run(debug=True)
