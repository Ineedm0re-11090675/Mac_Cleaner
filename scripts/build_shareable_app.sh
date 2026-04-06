#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ICON_SOURCE="$PROJECT_ROOT/assets/panda-icon.jpeg"
ICONSET_DIR="$PROJECT_ROOT/build/AppIcon.iconset"
ICON_FILE="$PROJECT_ROOT/assets/AppIcon.icns"
DIST_DIR="$PROJECT_ROOT/dist"
BUILD_DIR="$PROJECT_ROOT/build/pyinstaller"
APP_PATH="$DIST_DIR/macOS Cleaner.app"
ZIP_PATH="$DIST_DIR/macOS Cleaner-macOS.zip"
DESKTOP_ZIP="$HOME/Desktop/macOS Cleaner-macOS.zip"
DESKTOP_APP="$HOME/Desktop/macOS Cleaner.app"
APPLICATIONS_APP="$HOME/Applications/macOS Cleaner.app"

mkdir -p "$PROJECT_ROOT/build" "$DIST_DIR"

if [[ ! -f "$ICON_SOURCE" ]]; then
  echo "图标源文件不存在：$ICON_SOURCE" >&2
  exit 1
fi

echo "正在编译 C++ 核心..."
mkdir -p "$PROJECT_ROOT/build"
if clang++ -std=c++17 -O2 -arch arm64 -arch x86_64 -I"$PROJECT_ROOT/cpp/include" \
  "$PROJECT_ROOT/cpp/src/main.cpp" "$PROJECT_ROOT/cpp/src/cleaner.cpp" \
  -o "$PROJECT_ROOT/build/mac_cleaner" >/dev/null 2>&1; then
  echo "已生成通用二进制 mac_cleaner"
else
  echo "通用二进制编译失败，回退到当前机器架构..."
  clang++ -std=c++17 -O2 -I"$PROJECT_ROOT/cpp/include" \
    "$PROJECT_ROOT/cpp/src/main.cpp" "$PROJECT_ROOT/cpp/src/cleaner.cpp" \
    -o "$PROJECT_ROOT/build/mac_cleaner"
fi

echo "正在执行 Python 语法检查..."
python3 -m py_compile \
  "$PROJECT_ROOT/python/permission_manager.py" \
  "$PROJECT_ROOT/python/overview_manager.py" \
  "$PROJECT_ROOT/python/desktop_app/window.py" \
  "$PROJECT_ROOT/python/desktop_app/main.py" \
  "$PROJECT_ROOT/scripts/desktop_theme_smoke.py"

echo "正在执行桌面端主题离屏检查..."
QT_QPA_PLATFORM=offscreen python3 "$PROJECT_ROOT/scripts/desktop_theme_smoke.py" >/dev/null

if ! python3 -m pip show pyinstaller >/dev/null 2>&1; then
  echo "正在安装 PyInstaller..."
  python3 -m pip install --user pyinstaller
fi

rm -rf "$ICONSET_DIR"
mkdir -p "$ICONSET_DIR"
sips -s format png -z 16 16 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_16x16.png" >/dev/null
sips -s format png -z 32 32 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_16x16@2x.png" >/dev/null
sips -s format png -z 32 32 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_32x32.png" >/dev/null
sips -s format png -z 64 64 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_32x32@2x.png" >/dev/null
sips -s format png -z 128 128 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_128x128.png" >/dev/null
sips -s format png -z 256 256 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_128x128@2x.png" >/dev/null
sips -s format png -z 256 256 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_256x256.png" >/dev/null
sips -s format png -z 512 512 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_256x256@2x.png" >/dev/null
sips -s format png -z 512 512 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_512x512.png" >/dev/null
sips -s format png -z 1024 1024 "$ICON_SOURCE" --out "$ICONSET_DIR/icon_512x512@2x.png" >/dev/null
iconutil -c icns "$ICONSET_DIR" -o "$ICON_FILE"

rm -rf "$BUILD_DIR" "$DIST_DIR/macOS Cleaner" "$APP_PATH"
python3 -m PyInstaller \
  --noconfirm \
  --clean \
  --distpath "$DIST_DIR" \
  --workpath "$BUILD_DIR" \
  "$PROJECT_ROOT/packaging/macos_cleaner.spec"

codesign --force --deep --sign - "$APP_PATH" >/dev/null 2>&1 || true
rm -rf "$DESKTOP_APP" "$APPLICATIONS_APP"
rm -f "$ZIP_PATH" "$DESKTOP_ZIP"
ditto -c -k --sequesterRsrc --keepParent "$APP_PATH" "$ZIP_PATH"
cp -R "$APP_PATH" "$DESKTOP_APP"
cp "$ZIP_PATH" "$DESKTOP_ZIP"

echo "已生成可分享版本："
echo "  应用包：$APP_PATH"
echo "  压缩包：$ZIP_PATH"
echo "  桌面应用：$DESKTOP_APP"
echo "  桌面副本：$DESKTOP_ZIP"
