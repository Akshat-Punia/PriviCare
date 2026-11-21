"""
PriviCare — Windows Installer (.msi) Builder.

Packages the standalone compiled PriviCare.exe into a standard
Windows Installer (.msi) package for enterprise hospital deployment:
- Creates Program Files installation under ProgramFilesFolder\\PriviCare
- Adds Desktop Shortcut with custom PriviCare application icon
- Adds Start Menu Shortcut under Programs
- Registers ARPPRODUCTICON for Windows Installed Apps list
- DPDP Act 2023 & US HIPAA Safe Harbor Zero-Trust Workstation
"""

import os
import sys
import msilib
from msilib import schema, sequence


def build_msi():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "dist")
    assets_dir = os.path.join(base_dir, "assets")
    exe_path = os.path.join(dist_dir, "PriviCare.exe")
    msi_path = os.path.join(dist_dir, "PriviCare_Setup.msi")
    icon_path = os.path.join(assets_dir, "icon.ico")

    if not os.path.exists(exe_path):
        print(f"[ERROR] Executable not found at {exe_path}. Run PyInstaller first.")
        sys.exit(1)

    if os.path.exists(msi_path):
        try:
            os.remove(msi_path)
        except OSError:
            pass

    product_code = "{A2C4E8F1-3B5D-4A6C-9E7F-2D1B0C8A5E3F}"
    upgrade_code = "{B3D5F9A2-4C6E-5B7D-AE8F-3E2C1D9B6F4A}"
    product_name = "PriviCare"
    company_name = "PriviCare Healthcare Technologies"
    version = "2.0.0"

    print(f"[PriviCare] Generating Windows Installer (.msi): {msi_path}...")

    db = msilib.init_database(
        msi_path,
        schema,
        product_name,
        product_code,
        version,
        company_name
    )

    msilib.add_tables(db, sequence)

    feature = msilib.Feature(
        db,
        "PriviCareFeature",
        "PriviCare Clinical Intelligence Suite",
        "Installs PriviCare Doctor Clinical Intelligence & Secure RAG Suite",
        1
    )

    cab = msilib.CAB("PriviCareCabinet")

    # Directory Hierarchy: TARGETDIR -> ProgramFilesFolder -> PriviCare
    root_dir = msilib.Directory(db, cab, None, dist_dir, "TARGETDIR", "SourceDir")
    pfiles_dir = msilib.Directory(db, cab, root_dir, ".", "ProgramFilesFolder", "PFiles")
    app_dir = msilib.Directory(db, cab, pfiles_dir, ".", "PriviCare", "PriviCare")

    # Shell Shortcut folders
    desktop_dir = msilib.Directory(db, cab, root_dir, ".", "DesktopFolder", "Desktop")
    startmenu_dir = msilib.Directory(db, cab, root_dir, ".", "ProgramMenuFolder", "StartMenu")

    # Primary application executable component
    app_dir.start_component("PriviCareComponent", flags=0, feature=feature, keyfile="PriviCare.exe")
    app_dir.add_file("PriviCare.exe")

    # Add Application Icon & Shortcuts if icon exists
    if os.path.exists(icon_path):
        icon_id = "PriviCareAppIcon.exe"
        msilib.add_data(db, "Icon", [(icon_id, msilib.Binary(icon_path))])
        msilib.add_data(db, "Property", [
            ("UpgradeCode", upgrade_code),
            ("ALLUSERS", "1"),
            ("ARPPRODUCTICON", icon_id),
            ("ARPHELPLINK", "https://github.com/Akshat-Punia/Healthcare-PII-Anonymization-for-RAG-Pipelines"),
            ("ARPCOMMENTS", "PriviCare — Care in Every Data Beat. Zero-Trust HIPAA & India DPDP Act Healthcare Workstation"),
            ("ARPCONTACT", "PriviCare Healthcare Technologies"),
            ("ARPURLINFOABOUT", "https://github.com/Akshat-Punia/Healthcare-PII-Anonymization-for-RAG-Pipelines"),
        ])
        msilib.add_data(db, "Shortcut", [
            (
                "DesktopShortcut",
                "DesktopFolder",
                "PriviCare",
                "PriviCareComponent",
                "[#PriviCare.exe]",
                None,
                "PriviCare — Care in Every Data Beat",
                None,
                icon_id,
                0,
                1,
                "PriviCare"
            ),
            (
                "StartMenuShortcut",
                "ProgramMenuFolder",
                "PriviCare",
                "PriviCareComponent",
                "[#PriviCare.exe]",
                None,
                "PriviCare — Care in Every Data Beat",
                None,
                icon_id,
                0,
                1,
                "PriviCare"
            )
        ])
    else:
        msilib.add_data(db, "Property", [
            ("UpgradeCode", upgrade_code),
            ("ALLUSERS", "1"),
        ])

    cab.commit(db)
    db.Commit()

    import shutil
    v_msi_path = os.path.join(dist_dir, f"PriviCare_{version}_Setup.msi")
    shutil.copy2(msi_path, v_msi_path)

    size_mb = os.path.getsize(msi_path) / (1024 * 1024)
    print(f"[SUCCESS] PriviCare Windows Installer generated: {msi_path} ({size_mb:.2f} MB)")
    print(f"  * Versioned Copy: {v_msi_path}")
    print(f"  * Product: PriviCare v{version}")
    print(f"  * Desktop Shortcut: Enabled ('PriviCare')")
    print(f"  * Start Menu Shortcut: Enabled ('PriviCare')")
    print(f"  * Installed Apps Icon: Embedded")
    print(f"  * Install Location: C:\\Program Files\\PriviCare\\")


if __name__ == "__main__":
    build_msi()
