"""
PriviCare — Master Build Script.

Builds all 3 installer deliverables:
  1. PriviCare.exe        — Standalone application (PyInstaller onefile)
  2. PriviCare_Setup.msi  — Windows Installer Package (msilib)
  3. PriviCare_Setup.exe  — Setup application (PyInstaller + tkinter GUI installer)

Usage:
  python build_all.py          # Build all 3 deliverables
  python build_all.py --exe    # Build only the standalone exe
  python build_all.py --msi    # Build only the MSI package
  python build_all.py --setup  # Build only the Setup.exe
"""

import os
import sys
import time
import subprocess


def banner():
    print()
    print("=" * 70)
    print("  PRIVICARE BUILD SYSTEM — Care in Every Data Beat")
    print("  Building Windows Installer Packages...")
    print("=" * 70)
    print()


def build_exe():
    """Step 1: Build standalone PriviCare.exe with PyInstaller."""
    print("[STEP 1/3] Building PriviCare.exe with PyInstaller...")
    spec_file = os.path.join(os.path.dirname(__file__), "PriviCare.spec")
    if not os.path.exists(spec_file):
        print(f"  [ERROR] {spec_file} not found.")
        return False
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", spec_file],
        capture_output=True, text=True
    )
    exe_path = os.path.join("dist", "PriviCare.exe")
    if os.path.exists(exe_path):
        size = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"  [OK] PriviCare.exe — {size:.1f} MB")
        return True
    else:
        print(f"  [FAIL] Build failed. Error: {result.stderr[-300:] if result.stderr else 'unknown'}")
        return False


def build_msi():
    """Step 2: Build PriviCare_Setup.msi with msilib."""
    print("[STEP 2/3] Building PriviCare_Setup.msi...")
    result = subprocess.run(
        [sys.executable, "build_msi.py"],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"  [FAIL] {result.stderr}")
        return False
    return True


def build_setup():
    """Step 3: Build PriviCare_Setup.exe with embedded installer."""
    print("[STEP 3/3] Building PriviCare_Setup.exe...")
    result = subprocess.run(
        [sys.executable, "build_setup_exe.py"],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"  [FAIL] {result.stderr}")
        return False
    return True


def show_results():
    dist_dir = os.path.join(os.path.dirname(__file__), "dist")
    print()
    print("=" * 70)
    print("  BUILD RESULTS")
    print("=" * 70)
    
    files = [
        ("PriviCare.exe", "Application"),
        ("PriviCare_Setup.msi", "Windows Installer Package"),
        ("PriviCare_Setup.exe", "Setup Application"),
    ]
    
    for fname, ftype in files:
        fpath = os.path.join(dist_dir, fname)
        if os.path.exists(fpath):
            size_kb = os.path.getsize(fpath) / 1024
            if size_kb > 1024:
                size_str = f"{size_kb / 1024:.1f} MB"
            else:
                size_str = f"{size_kb:.0f} KB"
            print(f"  ✓ {fname:<25} {ftype:<30} {size_str}")
        else:
            print(f"  ✗ {fname:<25} {ftype:<30} NOT BUILT")
    
    print("=" * 70)
    print()


def main():
    banner()
    
    args = sys.argv[1:]
    build_all = len(args) == 0
    
    if build_all or "--exe" in args:
        build_exe()
    
    if build_all or "--msi" in args:
        build_msi()
    
    if build_all or "--setup" in args:
        build_setup()
    
    show_results()


if __name__ == "__main__":
    main()
