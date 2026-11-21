"""
PriviCare — Full Application Setup.exe Installer Builder.

Packages the complete PriviCare application into a self-extracting Windows installer:
  1. PriviCare.exe      — Main native desktop application
  2. assets/            — High-resolution logos, branding, and icons
  3. backend/           — Complete clinical RAG engine, patient records, PII vault, OCR & benchmarks
  4. run_app.bat        — Fast local launcher
  5. README.md          — Documentation
  6. icon.ico           — Application icon & shortcuts

Installs to user-selected folder (default: C:\\Program Files\\PriviCare).
Creates Desktop shortcut, Start Menu shortcut, and registers in Add/Remove Programs.
"""

import os
import sys
import shutil
import subprocess

INSTALLER_CODE = r'''"""PriviCare Installer — Self-Extracting Setup Application."""
import os
import sys
import shutil
import ctypes
import winreg
import subprocess

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def create_shortcut(shortcut_path, target_path, icon_path=None, description=""):
    """Create a Windows shortcut (.lnk) using PowerShell."""
    try:
        ps_parts = [
            "$ws = New-Object -ComObject WScript.Shell",
            '$s = $ws.CreateShortcut("' + shortcut_path.replace("\\", "\\\\") + '")',
            '$s.TargetPath = "' + target_path.replace("\\", "\\\\") + '"',
            '$s.WorkingDirectory = "' + os.path.dirname(target_path).replace("\\", "\\\\") + '"',
            '$s.Description = "' + description + '"',
        ]
        if icon_path and os.path.exists(icon_path):
            ps_parts.append('$s.IconLocation = "' + icon_path.replace("\\", "\\\\") + '"')
        ps_parts.append("$s.Save()")
        ps_cmd = "; ".join(ps_parts)
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)
        return True
    except Exception:
        return False

def register_uninstaller(install_dir, exe_path, icon_path, version="2.0.0"):
    """Register PriviCare in Add/Remove Programs."""
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\PriviCare"
        uninstall_cmd = 'cmd /c rmdir /s /q "' + install_dir + '"'
        root_key = winreg.HKEY_LOCAL_MACHINE if is_admin() else winreg.HKEY_CURRENT_USER
        with winreg.CreateKey(root_key, key_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "PriviCare")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, version)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "PriviCare Healthcare Technologies")
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, uninstall_cmd)
            if icon_path and os.path.exists(icon_path):
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon_path)
            exe_size = os.path.getsize(exe_path) // 1024 if os.path.exists(exe_path) else 60000
            winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, exe_size)
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "HelpLink", 0, winreg.REG_SZ,
                            "https://github.com/Akshat-Punia/Healthcare-PII-Anonymization-for-RAG-Pipelines")
        return True
    except Exception:
        return False

def show_gui_installer():
    """Show a graphical installer wizard."""
    import tkinter as tk
    from tkinter import filedialog

    result = {"install_dir": None, "create_desktop": True, "create_startmenu": True, "launch_after": True}

    root = tk.Tk()
    root.title("PriviCare Setup — Doctor Clinical Intelligence Suite")
    root.geometry("540x500")
    root.resizable(False, False)
    root.configure(bg="#0a1628")

    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - 270
    y = (root.winfo_screenheight() // 2) - 250
    root.geometry("+{}+{}".format(x, y))

    header = tk.Frame(root, bg="#0f2040", height=110)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(header, text="PriviCare", font=("Segoe UI", 24, "bold"),
             fg="#00bfff", bg="#0f2040").pack(pady=(15, 0))
    tk.Label(header, text="Care in Every Data Beat — Doctor Clinical Intelligence & Secure RAG",
             font=("Segoe UI", 10), fg="#7ec8e3", bg="#0f2040").pack()

    body = tk.Frame(root, bg="#0a1628", padx=30, pady=20)
    body.pack(fill="both", expand=True)

    tk.Label(body, text="Install PriviCare on your Computer",
             font=("Segoe UI", 12, "bold"), fg="white", bg="#0a1628").pack(anchor="w")
    tk.Label(body, text="Installs the full PriviCare application, clinical engine, patient database,\n"
                        "and local secure RAG models directly to your HDD/SSD for zero-trust operation.",
             font=("Segoe UI", 9), fg="#aabbcc", bg="#0a1628", justify="left").pack(anchor="w", pady=(5, 15))

    tk.Label(body, text="Installation Directory:", font=("Segoe UI", 10, "bold"),
             fg="white", bg="#0a1628").pack(anchor="w")

    dir_frame = tk.Frame(body, bg="#0a1628")
    dir_frame.pack(fill="x", pady=(4, 12))

    default_dir = os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "PriviCare")
    dir_var = tk.StringVar(value=default_dir)
    dir_entry = tk.Entry(dir_frame, textvariable=dir_var, font=("Segoe UI", 9), width=42)
    dir_entry.pack(side="left", fill="x", expand=True)

    def browse_dir():
        d = filedialog.askdirectory(initialdir=os.environ.get("ProgramFiles", "C:\\"))
        if d:
            dir_var.set(os.path.join(d, "PriviCare"))

    tk.Button(dir_frame, text="Browse...", command=browse_dir, font=("Segoe UI", 9),
              bg="#1a3a5c", fg="white", relief="flat", padx=10).pack(side="right", padx=(5, 0))

    desktop_var = tk.BooleanVar(value=True)
    startmenu_var = tk.BooleanVar(value=True)
    launch_var = tk.BooleanVar(value=True)

    tk.Checkbutton(body, text="Create Desktop shortcut", variable=desktop_var,
                   font=("Segoe UI", 9), fg="white", bg="#0a1628", selectcolor="#1a3a5c",
                   activebackground="#0a1628", activeforeground="white").pack(anchor="w")
    tk.Checkbutton(body, text="Create Start Menu shortcut", variable=startmenu_var,
                   font=("Segoe UI", 9), fg="white", bg="#0a1628", selectcolor="#1a3a5c",
                   activebackground="#0a1628", activeforeground="white").pack(anchor="w")
    tk.Checkbutton(body, text="Launch PriviCare now", variable=launch_var,
                   font=("Segoe UI", 9), fg="white", bg="#0a1628", selectcolor="#1a3a5c",
                   activebackground="#0a1628", activeforeground="white").pack(anchor="w", pady=(0, 10))

    def install():
        result["install_dir"] = dir_var.get()
        result["create_desktop"] = desktop_var.get()
        result["create_startmenu"] = startmenu_var.get()
        result["launch_after"] = launch_var.get()
        root.destroy()

    def cancel():
        result["install_dir"] = None
        root.destroy()

    btn_frame = tk.Frame(root, bg="#0a1628", padx=30, pady=15)
    btn_frame.pack(fill="x")

    tk.Button(btn_frame, text="Cancel", command=cancel, font=("Segoe UI", 10),
              bg="#333", fg="white", relief="flat", padx=20, pady=5).pack(side="right")
    tk.Button(btn_frame, text="Install PriviCare", command=install, font=("Segoe UI", 10, "bold"),
              bg="#0066cc", fg="white", relief="flat", padx=25, pady=5).pack(side="right", padx=(0, 10))

    root.mainloop()
    return result

def main():
    print()
    print("=" * 65)
    print("      PRIVICARE INSTALLER  —  Care in Every Data Beat")
    print("=" * 65)
    print()

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    source_exe = os.path.join(bundle_dir, "PriviCare.exe")
    if not os.path.exists(source_exe):
        source_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "PriviCare.exe")

    source_assets = os.path.join(bundle_dir, "assets")
    if not os.path.exists(source_assets):
        source_assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

    source_backend = os.path.join(bundle_dir, "backend")
    if not os.path.exists(source_backend):
        source_backend = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")

    source_bat = os.path.join(bundle_dir, "run_app.bat")
    if not os.path.exists(source_bat):
        source_bat = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_app.bat")

    source_readme = os.path.join(bundle_dir, "README.md")
    if not os.path.exists(source_readme):
        source_readme = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")

    if not os.path.exists(source_exe):
        print("[ERROR] PriviCare.exe payload missing from installer package.")
        input("Press Enter to exit...")
        sys.exit(1)

    try:
        opts = show_gui_installer()
    except Exception as e:
        default_dir = os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "PriviCare")
        user_input = input("Install directory [{}]: ".format(default_dir)).strip()
        opts = {
            "install_dir": user_input if user_input else default_dir,
            "create_desktop": True,
            "create_startmenu": True,
            "launch_after": True,
        }

    if not opts.get("install_dir"):
        print("[Cancelled] Installation cancelled.")
        sys.exit(0)

    install_dir = opts["install_dir"]
    print("\n[1/5] Preparing installation directory: {}".format(install_dir))
    try:
        os.makedirs(install_dir, exist_ok=True)
    except Exception as e:
        print("[Note] Installing to User AppData due to permissions: {}".format(e))
        install_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Programs", "PriviCare")
        os.makedirs(install_dir, exist_ok=True)

    # 1. Install PriviCare.exe
    dest_exe = os.path.join(install_dir, "PriviCare.exe")
    print("[2/5] Installing PriviCare Core Application ({:.1f} MB)...".format(os.path.getsize(source_exe) / 1024 / 1024))
    shutil.copy2(source_exe, dest_exe)

    # 2. Install Assets (logos, icons, badges)
    print("[3/5] Installing Application Assets & Clinical Data...")
    dest_assets = os.path.join(install_dir, "assets")
    if os.path.exists(source_assets):
        shutil.copytree(source_assets, dest_assets, dirs_exist_ok=True)

    # 3. Install Backend (clinical engine, patient database, models)
    dest_backend = os.path.join(install_dir, "backend")
    if os.path.exists(source_backend):
        shutil.copytree(source_backend, dest_backend, dirs_exist_ok=True)

    # 4. Install Runner batch & docs
    if os.path.exists(source_bat):
        shutil.copy2(source_bat, os.path.join(install_dir, "run_app.bat"))
    if os.path.exists(source_readme):
        shutil.copy2(source_readme, os.path.join(install_dir, "README.md"))

    # Icon file
    dest_icon = os.path.join(install_dir, "assets", "icon.ico")
    if not os.path.exists(dest_icon):
        dest_icon = os.path.join(install_dir, "icon.ico")
        if os.path.exists(os.path.join(source_assets, "icon.ico")):
            shutil.copy2(os.path.join(source_assets, "icon.ico"), dest_icon)

    # 4. Initialize Local Data Vault
    data_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "PriviCare")
    os.makedirs(os.path.join(data_dir, "data"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "lancedb"), exist_ok=True)

    # 5. Shortcuts
    print("[4/5] Creating Desktop & Start Menu shortcuts...")
    icon_for_lnk = dest_icon if os.path.exists(dest_icon) else dest_exe

    if opts.get("create_desktop"):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop, "PriviCare.lnk")
        if create_shortcut(shortcut_path, dest_exe, icon_for_lnk, "PriviCare — Doctor Clinical Intelligence Suite"):
            print("  + Desktop shortcut created: PriviCare.lnk")

    if opts.get("create_startmenu"):
        startmenu = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs")
        sm_dir = os.path.join(startmenu, "PriviCare")
        os.makedirs(sm_dir, exist_ok=True)
        shortcut_path = os.path.join(sm_dir, "PriviCare.lnk")
        if create_shortcut(shortcut_path, dest_exe, icon_for_lnk, "PriviCare — Doctor Clinical Intelligence Suite"):
            print("  + Start Menu shortcut created: PriviCare")

    register_uninstaller(install_dir, dest_exe, icon_for_lnk)

    print("[5/5] Installation Complete!")
    print()
    print("=" * 65)
    print("  PriviCare has been installed successfully on your machine!")
    print("  Installed Location: {}".format(install_dir))
    print("  Components Installed:")
    print("    - PriviCare.exe (Doctor Clinical Suite native application)")
    print("    - assets/       (PriviCare high-res logos & branding)")
    print("    - backend/      (Clinical RAG engine & Patient repository)")
    print("    - run_app.bat   (Quick launch shortcut)")
    print("=" * 65)

    if opts.get("launch_after"):
        print("\n[PriviCare] Launching PriviCare now...")
        os.startfile(dest_exe)

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
'''


def build_setup_exe():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "dist")
    assets_dir = os.path.join(base_dir, "assets")
    backend_dir = os.path.join(base_dir, "backend")
    exe_path = os.path.join(dist_dir, "PriviCare.exe")
    icon_path = os.path.join(assets_dir, "icon.ico")
    bat_path = os.path.join(base_dir, "run_app.bat")
    readme_path = os.path.join(base_dir, "README.md")

    if not os.path.exists(exe_path):
        print(f"[ERROR] PriviCare.exe not found at {exe_path}. Run PyInstaller first.")
        sys.exit(1)

    print("[PriviCare] Building Complete Full-App Setup Installer...")

    # Write installer script
    installer_script = os.path.join(dist_dir, "_privicare_installer.py")
    with open(installer_script, "w", encoding="utf-8") as f:
        f.write(INSTALLER_CODE)

    # Spec file for installer bundling the full app
    setup_spec = os.path.join(dist_dir, "_setup.spec")
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    [r'{installer_script}'],
    pathex=[],
    binaries=[],
    datas=[
        (r'{exe_path}', '.'),
        (r'{assets_dir}', 'assets'),
        (r'{backend_dir}', 'backend'),
        (r'{bat_path}', '.'),
        (r'{readme_path}', '.'),
    ],
    hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'subprocess'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['lancedb', 'pyarrow', 'numpy', 'scipy', 'webview', 'clr', 'pythonnet'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PriviCare_2.0.0_Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'{icon_path}',
)
"""

    with open(setup_spec, "w", encoding="utf-8") as f:
        f.write(spec_content)

    print("  [1/2] Compiling Setup.exe with PyInstaller...")
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", setup_spec],
        capture_output=True, text=True, cwd=base_dir
    )

    built_exe = os.path.join(dist_dir, "PriviCare_2.0.0_Setup.exe")
    if not os.path.exists(built_exe):
        alt_path = os.path.join(base_dir, "dist", "PriviCare_2.0.0_Setup.exe")
        if os.path.exists(alt_path):
            shutil.move(alt_path, built_exe)

    # Sync alias if possible
    setup_alias = os.path.join(dist_dir, "PriviCare_Setup.exe")
    if os.path.exists(built_exe):
        try:
            shutil.copy2(built_exe, setup_alias)
        except Exception:
            pass

    # Cleanup temp
    for f_path in [installer_script, setup_spec]:
        if os.path.exists(f_path):
            try:
                os.remove(f_path)
            except OSError:
                pass

    if os.path.exists(built_exe):
        size_mb = os.path.getsize(built_exe) / (1024 * 1024)
        print(f"[SUCCESS] Complete Full-App Setup generated: {built_exe} ({size_mb:.2f} MB)")
    else:
        print(f"[ERROR] Setup build failed. Stderr: {result.stderr[-300:]}")
        sys.exit(1)


if __name__ == "__main__":
    build_setup_exe()
