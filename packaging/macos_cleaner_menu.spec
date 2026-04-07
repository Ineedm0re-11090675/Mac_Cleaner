# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


project_root = Path.cwd()
python_root = project_root / "python"
icon_path = project_root / "assets" / "AppIcon.icns"
status_item_helper_path = project_root / "build" / "libmacos_status_item.dylib"


bundle_binaries = []
if status_item_helper_path.exists():
    bundle_binaries.append((str(status_item_helper_path), "."))

a = Analysis(
    [str(python_root / "tray_helper" / "main.py")],
    pathex=[str(python_root)],
    binaries=bundle_binaries,
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name="macOS Cleaner Menu",
    debug=False,
    bootloader_ignore_signals=False,
    exclude_binaries=True,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path.exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="macOS Cleaner Menu",
)

app = BUNDLE(
    coll,
    name="macOS Cleaner Menu.app",
    icon=str(icon_path) if icon_path.exists() else None,
    bundle_identifier="com.codex.macoscleaner.menu",
    version="1.0.0",
    info_plist={
        "LSUIElement": True,
        "NSHighResolutionCapable": True,
    },
)
