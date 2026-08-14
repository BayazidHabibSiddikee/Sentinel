#!/usr/bin/env python3
# tools/timer.py — runs as its own process
# Usage: python timer.py --duration 300   (300 seconds = 5 minutes)

import os, sys, time, argparse
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def format_duration(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    parts = []
    if h: parts.append(f"{h} hour(s)")
    if m: parts.append(f"{m} minute(s)")
    if s: parts.append(f"{s} second(s)")
    return " ".join(parts) if parts else "0 seconds"


def play_alarm_sound():
    sound_path = Path(__file__).resolve().parent / "mixkit-classic-alarm-995.wav"
    if not sound_path.exists():
        return False

    import shutil
    import subprocess
    players = ["paplay", "aplay", "pw-play", "mpv", "cvlc", "mpg123"]
    for p in players:
        if shutil.which(p):
            try:
                if p == "mpv":
                    subprocess.run([p, "--no-video", str(sound_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif p == "cvlc":
                    subprocess.run([p, "--play-and-exit", str(sound_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.run([p, str(sound_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                continue
    return False


def run_timer(duration_seconds: int):
    if duration_seconds <= 0:
        print("SPEAK: Invalid duration.")
        sys.exit(1)

    label = format_duration(duration_seconds)
    target = datetime.now() + timedelta(seconds=duration_seconds)
    end_str = target.strftime('%H:%M:%S')

    print(f"→ Starting timer for [{label}]")
    print(f"SPEAK: Timer set for {label}. Goes off at {target.strftime('%I:%M %p')}.")
    sys.stdout.flush()

    while True:
        if datetime.now() >= target:
            print("SPEAK: Time's up!")
            sys.stdout.flush()
            print("SPEAK: Timer done!")
            sys.stdout.flush()
            play_alarm_sound()
            break
        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Countdown timer")
    parser.add_argument('--duration', type=int, required=True,
                        help='Duration in seconds (e.g. 300 = 5 minutes)')
    args = parser.parse_args()
    run_timer(args.duration)

