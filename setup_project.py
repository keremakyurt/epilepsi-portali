#!/usr/bin/env python
"""Project reorganization script - Phase 2 file movements"""
import os
import shutil
from pathlib import Path

project_root = Path(__file__).parent
print(f"Working in: {project_root}")

# Phase 2: Create directories
dirs_to_create = ["data", "models", "logs", "tests", "notebooks"]
for dir_name in dirs_to_create:
    dir_path = project_root / dir_name
    dir_path.mkdir(exist_ok=True)
    print(f"[OK] Created directory: {dir_name}/")

# Create .gitkeep in models
gitkeep_path = project_root / "models" / ".gitkeep"
gitkeep_path.touch(exist_ok=True)
print(f"[OK] Created: models/.gitkeep")

# Move CSV files to data/
csv_files = [
    "epilepsy_dataset.csv",
    "ilae_v2_dataset.csv",
    "ilae_v3_dataset.csv"
]

for csv_file in csv_files:
    src = project_root / csv_file
    dst = project_root / "data" / csv_file
    if src.exists():
        shutil.move(str(src), str(dst))
        print(f"[OK] Moved: {csv_file} -> data/")
    else:
        print(f"[SKIP] Not found: {csv_file}")

# Move PKL files to models/
pkl_files = [
    "knn_epilepsy_model.pkl",
    "scaler.pkl",
    "metadata.pkl"
]

for pkl_file in pkl_files:
    src = project_root / pkl_file
    dst = project_root / "models" / pkl_file
    if src.exists():
        shutil.move(str(src), str(dst))
        print(f"[OK] Moved: {pkl_file} -> models/")
    else:
        print(f"[SKIP] Not found: {pkl_file}")

# Delete backup directories
backup_dirs = ["yedek_modeller", "yedek_verisetleri"]
for backup_dir in backup_dirs:
    dir_path = project_root / backup_dir
    if dir_path.exists():
        shutil.rmtree(str(dir_path))
        print(f"[OK] Deleted: {backup_dir}/")
    else:
        print(f"[SKIP] Not found: {backup_dir}/")

print("\n[COMPLETE] Phase 2: Project Structure Reorganization")

