#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "旧的桌面启动器方案已废弃，改为生成真正可运行的打包版应用。"
exec "$SCRIPT_DIR/build_shareable_app.sh"
