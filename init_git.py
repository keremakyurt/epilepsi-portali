#!/usr/bin/env python
"""Initialize Git repository for the epilepsy_project"""
import subprocess
import os

project_dir = os.getcwd()
print(f"[INFO] Initializing Git in: {project_dir}")

# Initialize git
result = subprocess.run(["git", "init"], cwd=project_dir, capture_output=True, text=True)
if result.returncode == 0:
    print("[OK] Git repository initialized")
else:
    print(f"[ERROR] Git init failed: {result.stderr}")
    exit(1)

# Configure git user (local)
result = subprocess.run(["git", "config", "user.name", "AkyurtPc"], cwd=project_dir, capture_output=True, text=True)
if result.returncode == 0:
    print('[OK] Git user name set to "AkyurtPc"')
else:
    print(f"[ERROR] Git config failed: {result.stderr}")

result = subprocess.run(["git", "config", "user.email", "akyurtpc@example.com"], cwd=project_dir, capture_output=True, text=True)
if result.returncode == 0:
    print('[OK] Git user email set to "akyurtpc@example.com"')
else:
    print(f"[ERROR] Git config failed: {result.stderr}")

# Verify git config
result = subprocess.run(["git", "config", "--local", "--list"], cwd=project_dir, capture_output=True, text=True)
if result.returncode == 0:
    print("\n[INFO] Git local config:")
    for line in result.stdout.split('\n'):
        if line and ('user' in line or 'core' in line):
            print(f"  {line}")

# Stage all files
print("\n[INFO] Staging files...")
result = subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True, text=True)
if result.returncode == 0:
    print("[OK] All files staged")
else:
    print(f"[ERROR] git add failed: {result.stderr}")

# Create initial commit
print("\n[INFO] Creating initial commit...")
commit_msg = "Initial project structure: organize files, add requirements.txt and .gitignore\n\nCo-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
result = subprocess.run(["git", "commit", "-m", commit_msg], cwd=project_dir, capture_output=True, text=True)
if result.returncode == 0:
    print("[OK] Initial commit created")
    print(f"  {result.stdout.strip()}")
else:
    print(f"[ERROR] git commit failed: {result.stderr}")

# Check git log
print("\n[INFO] Git log:")
result = subprocess.run(["git", "log", "--oneline", "-5"], cwd=project_dir, capture_output=True, text=True)
if result.returncode == 0:
    print(result.stdout)

# Check git status
print("[INFO] Git status:")
result = subprocess.run(["git", "status"], cwd=project_dir, capture_output=True, text=True)
if result.returncode == 0:
    print(result.stdout)
