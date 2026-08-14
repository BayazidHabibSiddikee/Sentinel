#!/bin/bash
# Start RUET 3-2 Semester Attendance Dashboard

echo "🚀 Starting RUET 3-2 Semester Attendance Dashboard..."
echo "📊 Access at: http://localhost:8765"
echo "💡 Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")"
python3 main.py
