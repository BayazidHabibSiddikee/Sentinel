#!/usr/bin/env python3
"""
RUET 3-2 Semester Attendance Tracker — FastAPI Web App
22 Series | Roll: 2208053 | Mechatronics Engineering
Target: 90% attendance for extra 10 marks per subject | GPA 4.00 Mission
"""

import json
import os
import subprocess
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── App Setup ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="RUET 3-2 Attendance Tracker",
    description="GPA 4.00 Mission Dashboard",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
SEMESTER_DIR = BASE_DIR.parent
DATA_FILE = BASE_DIR / "attendance_data.json"

# ── Constants ──────────────────────────────────────────────────────────────────
TOTAL_DAYS = 65
TARGET_PERCENTAGE = 90

THEORY_COURSES = [
    {"code": "MTE 3201", "name": "Power Electronics and Drives",   "credits": 3.0},
    {"code": "MTE 3205", "name": "Hydraulic and Pneumatic Control","credits": 3.0},
    {"code": "ME 3255",  "name": "Machine Dynamics and Vibrations","credits": 3.0},
    {"code": "ME 3265",  "name": "Fluid Mechanics and Machinery",  "credits": 3.0},
    {"code": "EEE 3287", "name": "Network and Communication Systems","credits": 3.0},
]

SESSIONAL_COURSES = [
    {"code": "MTE 3200", "name": "Mechatronics Case Study",                   "credits": 1.0},
    {"code": "MTE 3202", "name": "Power Electronics and Drives Sessional",    "credits": 0.75},
    {"code": "MTE 3206", "name": "Hydraulic and Pneumatic Control Sessional", "credits": 0.75},
    {"code": "ME 3256",  "name": "Machine Dynamics and Vibrations Sessional", "credits": 0.75},
]

ALL_COURSES = THEORY_COURSES + SESSIONAL_COURSES

# Class routine for 22 Series (R-404)
# Period times:
#   P1: 8:00-8:50   P2: 8:50-9:40   P3: 9:40-10:30  [SHORT BREAK 10:30-10:50]
#   P4: 10:50-11:40 P5: 11:40-12:30 P6: 12:30-1:20  [RECESS 1:20-2:30]
#   P7: 2:30-3:20   P8: 3:20-4:10   P9: 4:10-5:00
# Sessionals occupy consecutive periods (2 or 3 hrs)
# Format: (period, time, course_code, teacher, note)
CLASS_ROUTINE = {
    "Saturday": [
        # P1-P3: Free
        (4,  "10:50–11:40", "MTE 3201", "SHA",       ""),
        (5,  "11:40–12:30", "MTE 3205", "DKS",       ""),
        (6,  "12:30–1:20",  "EEE 3287", "SM",        ""),
        (78, "2:30–4:10",   "MTE 3200", "RAL/AICSL", "2hr sessional"),
    ],
    "Sunday": [
        (1,   "8:00–8:50",   "ME 3265",  "MRA",      ""),
        (2,   "8:50–9:40",   "ME 3255",  "MEH",      ""),
        (3,   "9:40–10:30",  "MTE 3205", "DKS/FRB",  ""),
        (456, "10:50–1:20",  "MTE 3202", "SHA/PD",   "3hr sessional (RAL)"),
        # P7-P9: Free
    ],
    "Monday": [
        (123, "8:00–10:30",  "ME 3256",  "",         "3hr sessional (MLL)"),
        (4,   "10:50–11:40", "ME 3265",  "MRA/HHH",  ""),
        (5,   "11:40–12:30", "ME 3255",  "MRI",      ""),
        (6,   "12:30–1:20",  "MTE 3201", "PD",       ""),
        # P7-P9: Free
    ],
    "Tuesday": [
        # P1-P3: Free
        (4,   "10:50–11:40", "EEE 3287", "SI",       ""),
        (5,   "11:40–12:30", "MTE 3205", "FRB",      ""),
        (6,   "12:30–1:20",  "ME 3255",  "MEH/MRI",  ""),
        (789, "2:30–5:00",   "MTE 3206", "DKS/FRB",  "3hr sessional (AICSL)"),
    ],
    "Wednesday": [
        (1,  "8:00–8:50",   "EEE 3287", "SM",        ""),
        (2,  "8:50–9:40",   "ME 3265",  "HHH",       ""),
        (3,  "9:40–10:30",  "MTE 3201", "SHA/PD",    ""),
    ],
    "Thursday": [],
    "Friday":   [],
}

SYLLABUS = {
    "MTE 3201": {
        "title": "Power Electronics and Drives",
        "credits": 3.0,
        "topics": [
            "Power Semiconductor Switches: SCR, TRIAC, power BJT, power MOSFET, IGBT",
            "AC-DC Converters: Single phase semi/full converters with R, R-L load",
            "DC-DC Converters: Buck, Boost, Buck-Boost, Cuk regulators",
            "Inverters (DC-AC): Single phase half/full bridge VSI, PWM techniques",
            "AC-AC Converters: AC voltage controller, Cycloconverter, VFD",
            "DC Drives: Four quadrant operation, Chopper-fed DC motors",
            "AC Drives: Induction Motor Drives, V/F control, Synchronous Motor Drives",
        ],
        "key_books": ["Mohan – Power Electronics", "P.C. Sen", "G.K. Dubey"],
    },
    "MTE 3205": {
        "title": "Hydraulic and Pneumatic Control",
        "credits": 3.0,
        "topics": [
            "Hydraulic Fluids, Pumps: Types, Characteristics, Selection",
            "Hydraulic Actuators and Valves: Pressure, Flow and Direction Controls",
            "Hydraulic Circuit Design: Reciprocating, Quick return, Sequencing, Synchronizing",
            "Pneumatic Compressors: Types, Characteristics",
            "Pneumatic Circuit Design: Classic, Cascade, Step counter, PLC control",
            "Electro-Pneumatic, Electro-Hydraulic and Robotic Circuits",
            "Maintenance of Hydraulic and Pneumatic Circuits",
        ],
        "key_books": ["S.R. Majumdar", "A. Esposito", "Anthony Esposito"],
    },
    "ME 3255": {
        "title": "Machine Dynamics and Vibrations",
        "credits": 3.0,
        "topics": [
            "Kinematics: Links, pairs, chains, Degrees of Freedom, Four bar mechanism",
            "Velocity and Acceleration analysis of mechanisms",
            "Belt, rope, chain drives, Gear systems, Gyroscopic motion",
            "Flywheel, Governors, Cams, Static and Dynamic Balancing",
            "Undamped free vibrations (1 & 2 DOF): longitudinal, transverse, torsional",
            "Damped free and forced vibrations (single DOF), Whirling of shafts",
            "Vibration measurement, Control Techniques, Active vibration absorber",
        ],
        "key_books": ["R.S. Khurmi", "J.J. Uicker", "Daniel J. Inman"],
    },
    "ME 3265": {
        "title": "Fluid Mechanics and Machinery",
        "credits": 3.0,
        "topics": [
            "Fluid Properties, Continuum, Classification",
            "Fluid Statics and Fluid Flow Concepts",
            "Bernoulli's Equation, Fluid Measurement, Viscous Flows",
            "Boundary Layers",
            "Rotodynamic and positive displacement machines",
            "Pumps, Turbines and Compressors: Operations and Performance",
            "Hydraulic Transmissions",
        ],
        "key_books": ["R.K. Bansal", "Frank M. White", "Jagdish Lal"],
    },
    "EEE 3287": {
        "title": "Network and Communication Systems",
        "credits": 3.0,
        "topics": [
            "Protocol Hierarchies, Data Link Control: HLDC, DLL in Internet",
            "LAN Protocols: IEEE 802, Switches, Hubs, Bridges, FDDI, Fast Ethernet",
            "Routing algorithms, Congestion Control, Internetworking, Wireless Networking",
            "GSM, WAP, WAN, CAN, Wireless Sensor Networks, Network Security",
            "Digital Communication, OSI Model, Serial/Parallel Communication Ports",
            "RS family, GPIB, USB, Ethernet, Industrial Buses, Fiber Optic",
            "Wi-Fi, Bluetooth, Satellite, ZigBee Networks for distributed Robots",
        ],
        "key_books": ["Forouzan", "Kurose & Ross", "Simon Haykin"],
    },
}

MARKS_BREAKDOWN = {
    "Class Tests (CT)": {"total": 20, "components": "4 CTs × 5 marks"},
    "Assignment":        {"total": 10, "components": "1 assignment"},
    "Attendance":        {"total": 10, "components": "90%+ = full marks"},
    "Final Exam":        {"total": 60, "components": "End semester exam"},
}

# ── Data Models ────────────────────────────────────────────────────────────────
class AttendanceRecord(BaseModel):
    date: str  # YYYY-MM-DD
    status: str  # present | absent | holiday
    courses_attended: List[str] = []
    notes: str = ""


class AttendanceUpdate(BaseModel):
    status: str
    courses_attended: List[str] = []
    notes: str = ""


class MarksEntry(BaseModel):
    course_code: str
    ct1: Optional[float] = None
    ct2: Optional[float] = None
    ct3: Optional[float] = None
    ct4: Optional[float] = None
    assignment: Optional[float] = None
    attendance_marks: Optional[float] = None
    final: Optional[float] = None


# ── Data Layer ─────────────────────────────────────────────────────────────────
def load_data() -> dict:
    if not DATA_FILE.exists():
        return {
            "start_date": str(date.today()),
            "attendance": [],
            "marks": {},
            "total_days": TOTAL_DAYS,
            "target_percentage": TARGET_PERCENTAGE,
        }
    try:
        with open(DATA_FILE) as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError):
        return {
            "start_date": str(date.today()),
            "attendance": [],
            "marks": {},
            "total_days": TOTAL_DAYS,
            "target_percentage": TARGET_PERCENTAGE,
        }
    # Migrate old data: add marks if missing
    if "marks" not in data:
        data["marks"] = {}
    return data


def save_data(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def compute_stats(data: dict) -> dict:
    att = data["attendance"]
    total = data["total_days"]
    target_pct = data["target_percentage"]

    present = sum(1 for r in att if r["status"] == "present")
    absent = sum(1 for r in att if r["status"] == "absent")
    holiday = sum(1 for r in att if r["status"] == "holiday")
    recorded = len(att)

    current_pct = round(present / total * 100, 2) if total > 0 else 0
    target_days = total * target_pct / 100  # e.g. 58.5
    needed = max(0, target_days - present)
    remaining = total - recorded
    req_remaining_pct = round(needed / remaining * 100, 2) if remaining > 0 else 0
    progress_to_target = round(present / target_days * 100, 2) if target_days > 0 else 0

    return {
        "total_days": total,
        "recorded_days": recorded,
        "present_days": present,
        "absent_days": absent,
        "holiday_days": holiday,
        "current_percentage": current_pct,
        "target_percentage": target_pct,
        "target_days": target_days,
        "remaining_days": remaining,
        "needed_present": needed,
        "required_percentage_remaining": req_remaining_pct,
        "progress_to_target": min(100, progress_to_target),
        "on_track": current_pct >= target_pct or req_remaining_pct <= 100,
        "achievable": req_remaining_pct <= 100,
    }


def compute_gpa_estimate(marks_data: dict) -> dict:
    """Estimate GPA based on entered marks."""
    results = {}
    for course in THEORY_COURSES:
        code = course["code"]
        m = marks_data.get(code, {})
        ct_total = sum(filter(None, [m.get("ct1"), m.get("ct2"), m.get("ct3"), m.get("ct4")]))
        total = ct_total + (m.get("assignment") or 0) + (m.get("attendance_marks") or 0) + (m.get("final") or 0)
        results[code] = {"total": round(total, 1), "name": course["name"]}
    return results


# ── API Routes ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the main dashboard HTML page."""
    html_path = BASE_DIR / "templates" / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text())
    return HTMLResponse("<h1>UI not found. Please run setup.</h1>")


@app.get("/api/stats")
async def get_stats():
    data = load_data()
    stats = compute_stats(data)
    gpa = compute_gpa_estimate(data["marks"])
    return {
        "stats": stats,
        "gpa_estimate": gpa,
        "start_date": data["start_date"],
        "today": str(date.today()),
        "today_day": date.today().strftime("%A"),
    }


@app.get("/api/attendance")
async def get_attendance():
    data = load_data()
    return {
        "records": sorted(data["attendance"], key=lambda x: x["date"], reverse=True),
        "stats": compute_stats(data),
    }


@app.post("/api/attendance")
async def add_attendance(record: AttendanceRecord):
    data = load_data()
    # Validate date
    try:
        datetime.strptime(record.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    # Check duplicate
    for existing in data["attendance"]:
        if existing["date"] == record.date:
            raise HTTPException(status_code=409, detail=f"Attendance already marked for {record.date}")
    # Validate status
    if record.status not in ("present", "absent", "holiday"):
        raise HTTPException(status_code=400, detail="Status must be: present, absent, or holiday")

    data["attendance"].append(record.model_dump())
    save_data(data)
    return {"message": f"Attendance marked: {record.date} → {record.status}", "stats": compute_stats(data)}


@app.put("/api/attendance/{record_date}")
async def update_attendance(record_date: str, update: AttendanceUpdate):
    data = load_data()
    for record in data["attendance"]:
        if record["date"] == record_date:
            record["status"] = update.status
            record["courses_attended"] = update.courses_attended
            record["notes"] = update.notes
            save_data(data)
            return {"message": f"Updated: {record_date}", "stats": compute_stats(data)}
    raise HTTPException(status_code=404, detail=f"No record found for {record_date}")


@app.delete("/api/attendance/{record_date}")
async def delete_attendance(record_date: str):
    data = load_data()
    original_len = len(data["attendance"])
    data["attendance"] = [r for r in data["attendance"] if r["date"] != record_date]
    if len(data["attendance"]) == original_len:
        raise HTTPException(status_code=404, detail=f"No record found for {record_date}")
    save_data(data)
    return {"message": f"Deleted: {record_date}", "stats": compute_stats(data)}


@app.get("/api/routine")
async def get_routine():
    today = date.today().strftime("%A")
    return {
        "routine": CLASS_ROUTINE,
        "today": today,
        "today_classes": CLASS_ROUTINE.get(today, []),
    }


@app.get("/api/courses")
async def get_courses():
    return {
        "theory": THEORY_COURSES,
        "sessional": SESSIONAL_COURSES,
        "syllabus": SYLLABUS,
        "marks_breakdown": MARKS_BREAKDOWN,
        "total_credits": 18.25,
    }


@app.get("/api/marks")
async def get_marks():
    data = load_data()
    return {"marks": data["marks"], "gpa_estimate": compute_gpa_estimate(data["marks"])}


@app.post("/api/marks")
async def update_marks(entry: MarksEntry):
    data = load_data()
    code = entry.course_code
    if code not in [c["code"] for c in THEORY_COURSES]:
        raise HTTPException(status_code=400, detail=f"Unknown course: {code}")
    data["marks"][code] = entry.model_dump(exclude={"course_code"})
    save_data(data)
    return {"message": f"Marks updated for {code}", "gpa_estimate": compute_gpa_estimate(data["marks"])}


@app.get("/api/syllabus/{course_code}")
async def get_syllabus(course_code: str):
    course_code = course_code.upper().replace("-", " ")
    if course_code not in SYLLABUS:
        raise HTTPException(status_code=404, detail=f"Course not found: {course_code}")
    return SYLLABUS[course_code]


@app.get("/api/today-check")
async def today_check():
    """Check if today's attendance has been marked."""
    data = load_data()
    today = str(date.today())
    today_day = date.today().strftime("%A")
    record = next((r for r in data["attendance"] if r["date"] == today), None)
    today_classes = CLASS_ROUTINE.get(today_day, [])
    return {
        "today": today,
        "day": today_day,
        "marked": record is not None,
        "record": record,
        "has_classes": len(today_classes) > 0,
        "classes_count": len(today_classes),
        "classes": today_classes,
    }


class OpenFileRequest(BaseModel):
    path: str  # relative to SEMESTER_DIR, or absolute


@app.post("/api/open-file")
async def open_file(req: OpenFileRequest):
    """Open a file or folder using xdg-open (system default application)."""
    p = Path(req.path)
    if not p.is_absolute():
        p = SEMESTER_DIR / p
    p = p.resolve()

    # Security: must be inside SEMESTER_DIR
    try:
        p.relative_to(SEMESTER_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Path outside allowed directory")

    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {p}")

    try:
        subprocess.Popen(["xdg-open", str(p)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"message": f"Opened: {p.name}", "path": str(p)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open: {e}")


@app.get("/api/semester-files")
async def get_semester_files():
    """Return structured list of all course PDFs and folders for the Resources section."""
    base = SEMESTER_DIR.resolve()

    def rel(p: Path) -> str:
        return str(p.relative_to(base))

    courses = {}
    for code in ["MTE 3201", "MTE 3205", "ME 3255", "ME 3265", "EEE 3287", "MTE 3200"]:
        course_dir = base / code
        if not course_dir.exists():
            continue
        pdfs = []
        folders = []
        for item in sorted(course_dir.rglob("*.pdf"), key=lambda x: x.name):
            pdfs.append({"name": item.name, "rel": rel(item), "size_kb": round(item.stat().st_size / 1024)})
        for item in sorted(course_dir.iterdir()):
            if item.is_dir():
                folders.append({"name": item.name, "rel": rel(item)})
        courses[code] = {"pdfs": pdfs, "folders": folders}

    root_pdfs = [{"name": f.name, "rel": rel(f)} for f in sorted(base.glob("*.pdf"))]

    questions = {"prev": [], "final": []}
    prev_dir = base / "Questions" / "Previous Year Questions"
    if prev_dir.exists():
        questions["prev"] = [{"name": f.name, "rel": rel(f)} for f in sorted(prev_dir.glob("*.pdf"))]
    final_dir = base / "Questions" / "Semester Final Questions (20 Series)"
    if final_dir.exists():
        questions["final"] = [{"name": f.name, "rel": rel(f)} for f in sorted(final_dir.glob("*.pdf"))]

    assignments = []
    assign_base = base / "Assignments"
    if assign_base.exists():
        for course_dir in sorted(assign_base.iterdir()):
            if course_dir.is_dir():
                for f in course_dir.glob("*.pdf"):
                    assignments.append({"course": course_dir.name, "name": f.name, "rel": rel(f)})

    # Sessional lab reports
    sessionals = []
    sess_base = base / "Sessionals"
    if sess_base.exists():
        for sess_dir in sorted(sess_base.iterdir()):
            if sess_dir.is_dir():
                for f in sorted(sess_dir.rglob("*.pdf"), key=lambda x: x.name):
                    sessionals.append({"course": sess_dir.name, "name": f.name, "rel": rel(f)})

    return {
        "courses": courses,
        "root_pdfs": root_pdfs,
        "questions": questions,
        "assignments": assignments,
        "sessionals": sessionals,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8765, reload=False, log_level="info")
