#!/usr/bin/env python3
"""
RUET 3-2 Semester Attendance Tracker
Target: 90% attendance for extra 10 marks per subject
Total working days: 65
Already lost: 10 days (2 weeks)
Must attend: 48.5 out of remaining 55 days

Usage:
    python attendance_tracker.py
"""

import json
import os
from datetime import datetime, timedelta
from colorama import init, Fore, Style

# Initialize colorama
init()

# Configuration
TOTAL_DAYS = 65
DAYS_LOST = 10
DAYS_REMAINING = TOTAL_DAYS - DAYS_LOST
TARGET_ATTENDANCE = 58.5  # 90% of 65
CURRENT_ATTENDANCE = 48.5  # Must attend from remaining 55 days

# Courses in 3-2 semester
THEORY_COURSES = [
    "MTE 3201 - Power Electronics and Drives",
    "MTE 3205 - Hydraulic and Pneumatic Control",
    "ME 3255 - Machine Dynamics and Vibrations",
    "ME 3265 - Fluid Mechanics and Machinery",
    "EEE 3287 - Network and Communication Systems"
]

SESSIONAL_COURSES = [
    "MTE 3200 - Mechatronics Case Study",
    "MTE 3202 - Power Electronics and Drives Sessional",
    "MTE 3206 - Hydraulic and Pneumatic Control Sessional",
    "ME 3256 - Machine Dynamics and Vibrations Sessional"
]

# Data file
data_file = "attendance_data.json"


def load_data():
    """Load attendance data from file"""
    if not os.path.exists(data_file):
        return {
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "attendance": [],
            "total_days": TOTAL_DAYS,
            "days_lost": DAYS_LOST,
            "target_percentage": 90
        }
    with open(data_file, 'r') as f:
        return json.load(f)


def save_data(data):
    """Save attendance data to file"""
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)


def mark_attendance(date, status, courses_attended=None):
    """
    Mark attendance for a day
    status: 'present', 'absent', 'holiday'
    courses_attended: list of course codes attended (for partial days)
    """
    data = load_data()
    
    # Check if date already exists
    for record in data['attendance']:
        if record['date'] == date:
            print(f"{Fore.YELLOW}Attendance already marked for {date}{Style.RESET_ALL}")
            return False
    
    record = {
        'date': date,
        'status': status,
        'courses_attended': courses_attended or [],
        'notes': ''
    }
    
    data['attendance'].append(record)
    save_data(data)
    return True


def get_attendance_stats():
    """Calculate attendance statistics"""
    data = load_data()
    
    total_records = len(data['attendance'])
    present_days = sum(1 for r in data['attendance'] if r['status'] == 'present')
    absent_days = sum(1 for r in data['attendance'] if r['status'] == 'absent')
    holiday_days = sum(1 for r in data['attendance'] if r['status'] == 'holiday')
    
    current_percentage = (present_days / data['total_days']) * 100 if total_records > 0 else 0
    
    # Calculate remaining days
    remaining_days = data['total_days'] - total_records
    needed_present = max(0, data['target_percentage'] * data['total_days'] / 100 - present_days)
    
    return {
        'total_days': data['total_days'],
        'recorded_days': total_records,
        'present_days': present_days,
        'absent_days': absent_days,
        'holiday_days': holiday_days,
        'current_percentage': current_percentage,
        'remaining_days': remaining_days,
        'needed_present': needed_present,
        'required_percentage_remaining': (needed_present / remaining_days * 100) if remaining_days > 0 else 0
    }


def print_dashboard():
    """Print attendance dashboard"""
    stats = get_attendance_stats()
    
    print(f"\n{Fore.CYAN}╔{'═' * 70}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{'RUET 3-2 SEMESTER ATTENDANCE TRACKER':^70}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{'Target: 90% for Extra 10 Marks per Subject':^70}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 70}╝{Style.RESET_ALL}\n")
    
    # Current Status
    print(f"{Fore.MAGENTA}📊 CURRENT STATUS{Style.RESET_ALL}")
    print(f"{'─' * 70}")
    print(f"| {'Total Working Days:':<30} | {stats['total_days']:<10} |")
    print(f"| {'Days Recorded:':<30} | {stats['recorded_days']:<10} |")
    print(f"| {'Present Days:':<30} | {Fore.GREEN}{stats['present_days']}{Style.RESET_ALL:<10} |")
    print(f"| {'Absent Days:':<30} | {Fore.RED}{stats['absent_days']}{Style.RESET_ALL:<10} |")
    print(f"| {'Holiday Days:':<30} | {Fore.BLUE}{stats['holiday_days']}{Style.RESET_ALL:<10} |")
    print(f"| {'Current Attendance %:':<30} | {stats['current_percentage']:.1f}%{'':<6} |")
    print(f"{'─' * 70}\n")
    
    # Target Analysis
    print(f"{Fore.YELLOW}🎯 TARGET ANALYSIS{Style.RESET_ALL}")
    print(f"{'─' * 70}")
    print(f"| {'Days Remaining:':<30} | {stats['remaining_days']:<10} |")
    print(f"| {'Need to Attend:':<30} | {Fore.GREEN}{stats['needed_present']}{Style.RESET_ALL:<10} |")
    
    if stats['remaining_days'] > 0:
        required_pct = stats['required_percentage_remaining']
        if required_pct <= 100:
            pct_color = Fore.GREEN if required_pct <= 90 else Fore.YELLOW
            print(f"| {'Required % Remaining:':<30} | {pct_color}{required_pct:.1f}%{Style.RESET_ALL:<6} |")
        else:
            print(f"| {'Required % Remaining:':<30} | {Fore.RED}IMPOSSIBLE!{Style.RESET_ALL:<6} |")
    
    print(f"{'─' * 70}\n")
    
    # Progress Bar
    print(f"{Fore.CYAN}📈 PROGRESS TO 90%{Style.RESET_ALL}")
    print(f"{'─' * 70}")
    target = stats['total_days'] * 0.9
    progress = stats['present_days']
    bar_length = 50
    filled = int(bar_length * progress / target)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"|{bar}| {progress}/{target} ({progress/target*100:.1f}%)")
    print(f"{'─' * 70}\n")
    
    # Warning System
    if stats['current_percentage'] < 90:
        print(f"{Fore.RED}⚠️  WARNING: Current attendance below 90%!{Style.RESET_ALL}")
        if stats['remaining_days'] > 0:
            print(f"   {Fore.YELLOW}You need to attend {stats['required_percentage_remaining']:.1f}% of remaining days{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}✅ ON TRACK! Keep it up!{Style.RESET_ALL}")
    
    print()


def print_courses():
    """Print course list"""
    print(f"\n{Fore.CYAN}📚 THEORY COURSES (3-2 Semester){Style.RESET_ALL}")
    print(f"{'─' * 70}")
    for i, course in enumerate(THEORY_COURSES, 1):
        print(f"  {i}. {course}")
    
    print(f"\n{Fore.CYAN}🔬 SESSIONAL COURSES{Style.RESET_ALL}")
    print(f"{'─' * 70}")
    for i, course in enumerate(SESSIONAL_COURSES, 1):
        print(f"  {i}. {course}")
    print()


def mark_today():
    """Mark today's attendance"""
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{Fore.YELLOW}Marking attendance for: {today}{Style.RESET_ALL}")
    print(f"{'─' * 70}")
    print("  1. Present (All classes)")
    print("  2. Absent")
    print("  3. Holiday")
    print("  4. Partial Attendance")
    print(f"{'─' * 70}")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == '1':
        status = 'present'
        courses = THEORY_COURSES + SESSIONAL_COURSES
    elif choice == '2':
        status = 'absent'
        courses = []
    elif choice == '3':
        status = 'holiday'
        courses = []
    elif choice == '4':
        status = 'present'
        print("\nSelect courses attended:")
        all_courses = THEORY_COURSES + SESSIONAL_COURSES
        for i, course in enumerate(all_courses, 1):
            print(f"  {i}. {course}")
        selected = input("Enter course numbers (comma separated): ").strip()
        courses = [all_courses[int(x)-1] for x in selected.split(',') if x.strip()]
    else:
        print(f"{Fore.RED}Invalid choice!{Style.RESET_ALL}")
        return
    
    if mark_attendance(today, status, courses):
        print(f"{Fore.GREEN}✅ Attendance marked successfully!{Style.RESET_ALL}")
    
    print_dashboard()


def mark_specific_date():
    """Mark attendance for a specific date"""
    date_str = input("Enter date (YYYY-MM-DD): ").strip()
    
    # Validate date format
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print(f"{Fore.RED}Invalid date format! Use YYYY-MM-DD{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.YELLOW}Marking attendance for: {date_str}{Style.RESET_ALL}")
    print(f"{'─' * 70}")
    print("  1. Present (All classes)")
    print("  2. Absent")
    print("  3. Holiday")
    print(f"{'─' * 70}")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        status = 'present'
        courses = THEORY_COURSES + SESSIONAL_COURSES
    elif choice == '2':
        status = 'absent'
        courses = []
    elif choice == '3':
        status = 'holiday'
        courses = []
    else:
        print(f"{Fore.RED}Invalid choice!{Style.RESET_ALL}")
        return
    
    if mark_attendance(date_str, status, courses):
        print(f"{Fore.GREEN}✅ Attendance marked successfully!{Style.RESET_ALL}")
    
    print_dashboard()


def view_history():
    """View attendance history"""
    data = load_data()
    
    if not data['attendance']:
        print(f"\n{Fore.YELLOW}No attendance records yet!{Style.RESET_ALL}\n")
        return
    
    print(f"\n{Fore.CYAN}📜 ATTENDANCE HISTORY{Style.RESET_ALL}")
    print(f"{'─' * 70}")
    print(f"{'Date':<12} | {'Status':<10} | {'Courses Attended':<45}")
    print(f"{'─' * 70}")
    
    for record in sorted(data['attendance'], key=lambda x: x['date'], reverse=True):
        status_color = Fore.GREEN if record['status'] == 'present' else (
            Fore.RED if record['status'] == 'absent' else Fore.BLUE
        )
        courses = ', '.join(record['courses_attended'][:3]) + ('...' if len(record['courses_attended']) > 3 else '')
        print(f"{record['date']:<12} | {status_color}{record['status']:<10}{Style.RESET_ALL} | {courses:<45}")
    
    print(f"{'─' * 70}\n")


def edit_record():
    """Edit an existing attendance record"""
    data = load_data()
    
    if not data['attendance']:
        print(f"\n{Fore.YELLOW}No records to edit!{Style.RESET_ALL}\n")
        return
    
    print(f"\n{Fore.CYAN}Select record to edit:{Style.RESET_ALL}")
    for i, record in enumerate(data['attendance'], 1):
        print(f"  {i}. {record['date']} - {record['status']}")
    
    choice = input("Enter record number: ").strip()
    
    try:
        idx = int(choice) - 1
        record = data['attendance'][idx]
    except (ValueError, IndexError):
        print(f"{Fore.RED}Invalid choice!{Style.RESET_ALL}")
        return
    
    print(f"\nEditing: {record['date']} (Current: {record['status']})")
    print("  1. Present")
    print("  2. Absent")
    print("  3. Holiday")
    
    choice = input("Enter new status (1-3): ").strip()
    
    if choice == '1':
        new_status = 'present'
    elif choice == '2':
        new_status = 'absent'
    elif choice == '3':
        new_status = 'holiday'
    else:
        print(f"{Fore.RED}Invalid choice!{Style.RESET_ALL}")
        return
    
    data['attendance'][idx]['status'] = new_status
    save_data(data)
    print(f"{Fore.GREEN}✅ Record updated!{Style.RESET_ALL}")
    print_dashboard()


def main():
    """Main menu"""
    print_dashboard()
    
    while True:
        print(f"\n{Fore.CYAN}╔{'═' * 70}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{'MAIN MENU':^70}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 70}╝{Style.RESET_ALL}")
        print("  1. Mark Today's Attendance")
        print("  2. Mark Specific Date Attendance")
        print("  3. View Attendance History")
        print("  4. Edit Record")
        print("  5. View Courses")
        print("  6. Refresh Dashboard")
        print("  7. Exit")
        print(f"{'─' * 70}")
        
        choice = input("Enter choice (1-7): ").strip()
        
        if choice == '1':
            mark_today()
        elif choice == '2':
            mark_specific_date()
        elif choice == '3':
            view_history()
        elif choice == '4':
            edit_record()
        elif choice == '5':
            print_courses()
        elif choice == '6':
            print_dashboard()
        elif choice == '7':
            print(f"\n{Fore.GREEN}Good luck with your GPA 4.00 mission!{Style.RESET_ALL}\n")
            break
        else:
            print(f"{Fore.RED}Invalid choice!{Style.RESET_ALL}")


if __name__ == "__main__":
    # Check for colorama
    try:
        import colorama
    except ImportError:
        print("Colorama not found. Installing...")
        import subprocess
        subprocess.run(['pip', 'install', 'colorama'], check=True)
    
    main()
