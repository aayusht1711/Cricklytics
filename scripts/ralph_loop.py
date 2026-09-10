#!/usr/bin/env python3
"""
Ralph Loop Autonomous Task Runner for Antigravity
Usage: python scripts/ralph_loop.py [--max-iterations N]
"""

import os
import sys
import time
import subprocess
import argparse

TASK_FILE = "task.md"
PROGRESS_FILE = "progress.txt"

def ensure_state_files():
    if not os.path.exists(TASK_FILE):
        with open(TASK_FILE, "w", encoding="utf-8") as f:
            f.write("# Tasks\n\n- [ ] Initial workspace check\n")
        print(f"Created initial {TASK_FILE}")
        
    if not os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            f.write(f"--- Ralph Loop Started at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        print(f"Created {PROGRESS_FILE}")

def count_pending_tasks():
    if not os.path.exists(TASK_FILE):
        return 0
    with open(TASK_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    return content.count("- [ ]")

def log_progress(message):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {message}\n"
    print(line, end="")
    with open(PROGRESS_FILE, "a", encoding="utf-8") as f:
        f.write(line)

def run_verification():
    log_progress("Running verification build check...")
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
    if os.path.exists(frontend_dir):
        result = subprocess.run("npm run build", cwd=frontend_dir, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            log_progress("Frontend build PASSED.")
            return True
        else:
            log_progress(f"Frontend build FAILED:\n{result.stderr[:500]}")
            return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Ralph Loop Task Runner for Antigravity")
    parser.add_argument("--max-iterations", type=int, default=10, help="Maximum loop iterations")
    args = parser.parse_args()

    ensure_state_files()
    log_progress(f"Starting Ralph Loop execution (Max iterations: {args.max_iterations})...")

    iteration = 0
    while iteration < args.max_iterations:
        iteration += 1
        pending = count_pending_tasks()
        log_progress(f"Iteration {iteration}/{args.max_iterations} - Pending tasks: {pending}")
        
        if pending == 0:
            log_progress("All tasks completed in task.md! Exiting Ralph Loop successfully.")
            break

        # Verification step
        success = run_verification()
        if not success:
            log_progress("Build failure detected. Fix required before proceeding.")
            
        time.sleep(2)

    log_progress(f"Ralph Loop finished after {iteration} iteration(s).")

if __name__ == "__main__":
    main()
