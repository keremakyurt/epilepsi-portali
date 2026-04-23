#!/usr/bin/env python
"""Generate requirements.txt from the venv"""
import subprocess
import sys
import os

# Get the venv python executable
venv_python = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")

if not os.path.exists(venv_python):
    print(f"[ERROR] venv python not found at: {venv_python}")
    sys.exit(1)

print(f"[INFO] Using venv python: {venv_python}")

# Run pip freeze using the venv python
result = subprocess.run([venv_python, "-m", "pip", "freeze"], capture_output=True, text=True)

if result.returncode == 0:
    with open("requirements.txt", "w") as f:
        f.write(result.stdout)
    lines = result.stdout.strip().split('\n')
    print(f"[OK] Generated requirements.txt with {len(lines)} packages")
    print("\nFirst 10 packages:")
    for line in lines[:10]:
        print(f"  - {line}")
else:
    print(f"[ERROR] pip freeze failed:")
    print(result.stderr)
    sys.exit(1)
