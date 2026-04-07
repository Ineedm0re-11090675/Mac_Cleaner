# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


project_root = Path.cwd()
python_root = project_root / "python"
icon_path = project_root / "assets" / "AppIcon.icns"
binary_path = project_root / "build" / "mac_cleaner"
reopen_helper_path = project_root / "build" / "libmacos_reopen_hook.dylib"


bundle_binaries = [(str(binary_path), ".")]
if reopen_helper_path.exists():
    bundle_binaries.append((str(reopen_helper_path), "."))

a = Analysis(
    [str(python_root / "desktop_app" / "main.py")],
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
    name="macOS Cleaner",
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
    name="macOS Cleaner",
)

app = BUNDLE(
    coll,
    name="macOS Cleaner.app",
    icon=str(icon_path) if icon_path.exists() else None,
    bundle_identifier="com.codex.macoscleaner.desktop",
    version="1.1.0",
    info_plist={
        "NSDesktopFolderUsageDescription": "macOS Cleaner 需要访问桌面中的截图和图片，用于图片管理与磁盘分析。",
        "NSDocumentsFolderUsageDescription": "macOS Cleaner 需要访问文稿目录，用于磁盘空间分析和文件整理。",
        "NSDownloadsFolderUsageDescription": "macOS Cleaner 需要访问下载目录中的图片和文件，用于清理与整理功能。",
    },
)
