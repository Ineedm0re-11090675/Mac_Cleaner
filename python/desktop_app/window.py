from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from application_manager import clean_app_residuals, scan_app_residuals
from bridge import CleanerBridge
from disk_manager import scan_disk_usage
from image_manager import create_image_preview, scan_image_library
from memory_manager import scan_memory_processes, terminate_processes
from overview_manager import execute_overview_actions, scan_overview
from permission_manager import build_preflight_message, evaluate_feature_permissions, feature_directory_map
from settings_manager import APP_NAME, APP_VERSION, THEME_OPTIONS, get_settings_manager, open_system_settings
from startup_manager import disable_startup_items, scan_startup_items

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QGridLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QCheckBox,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


APP_STYLESHEET = """
QMainWindow {
    background: #edf3fb;
}

QWidget#AppRoot {
    background:
        qradialgradient(cx: 0.12, cy: 0.08, radius: 0.42, fx: 0.12, fy: 0.08,
            stop: 0 rgba(37, 99, 235, 0.12),
            stop: 1 rgba(237, 243, 251, 1.0));
}

QLabel {
    background: transparent;
    color: #152133;
}

QFrame#Sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0f1c34, stop:1 #162847);
    border: 1px solid rgba(127, 156, 212, 0.28);
    border-radius: 24px;
}

QFrame#ContentCard {
    background: #ffffff;
    border: 1px solid #d9e2ec;
    border-radius: 22px;
}

QFrame#InfoCard {
    background: #f8fbff;
    border: 1px solid #d9e2ec;
    border-radius: 18px;
}

QFrame#OverviewCard {
    background: #f8fbff;
    border: 1px solid #d9e2ec;
    border-radius: 18px;
}

QFrame#OverviewItemRow {
    background: #ffffff;
    border: 1px solid #dfe7f2;
    border-radius: 14px;
}

QLabel#BrandKicker,
QLabel#SidebarCopy,
QLabel#SidebarFooter {
    color: rgba(226, 236, 255, 0.82);
}

QLabel#BrandTitle {
    color: #ffffff;
    font-size: 28px;
    font-weight: 800;
}

QLabel#PageKicker {
    color: #5d79a8;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

QLabel#PageTitle {
    color: #132137;
    font-size: 30px;
    font-weight: 800;
}

QLabel#PageDescription {
    color: #55657f;
    font-size: 15px;
}

QLabel#SummaryLabel {
    background: #eef4ff;
    color: #2f4c77;
    border: 1px solid #d5e3fb;
    border-radius: 14px;
    padding: 10px 12px;
    font-weight: 600;
}

QLabel#TipsLabel {
    background: #fff4d6;
    color: #8a5800;
    border: 1px solid #f1d48a;
    border-radius: 14px;
    padding: 11px 12px;
    font-weight: 700;
}

QLabel#OverviewSectionTitle {
    color: #132137;
    font-size: 18px;
    font-weight: 800;
}

QLabel#OverviewCardTitle {
    color: #132137;
    font-size: 20px;
    font-weight: 800;
}

QLabel#OverviewCardBody {
    background: #ffffff;
    border: 1px solid #d9e2ec;
    border-radius: 14px;
    padding: 12px;
    color: #415570;
}

QLabel#OverviewItemTitle {
    color: #132137;
    font-size: 15px;
    font-weight: 800;
}

QLabel#OverviewItemNote {
    color: #132137;
    font-size: 13px;
}

QLabel#OverviewStatusBadge {
    padding: 6px 10px;
    border-radius: 999px;
    font-weight: 700;
}

QLabel#OverviewStatusBadge[severity="ok"] {
    background: rgba(22,163,74,0.12);
    color: #166534;
}

QLabel#OverviewStatusBadge[severity="issue"] {
    background: rgba(220,38,38,0.12);
    color: #991b1b;
}

QPushButton {
    border: 1px solid #d4ddea;
    border-radius: 12px;
    padding: 10px 14px;
    background: #ffffff;
    color: #182235;
    font-weight: 600;
}

QPushButton:hover {
    background: #f7fbff;
}

QPushButton:disabled {
    color: #8ea0ba;
    background: #f2f5fa;
}

QPushButton#NavButton {
    text-align: left;
    padding: 14px 16px;
    border-radius: 16px;
    border: 1px solid rgba(150, 176, 221, 0.18);
    background: rgba(255, 255, 255, 0.05);
    color: rgba(245, 248, 255, 0.98);
}

QPushButton#NavButton:hover {
    background: rgba(255, 255, 255, 0.1);
}

QPushButton#NavButton:checked {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #3a7af8, stop:1 #2457dc);
    border-color: rgba(111, 160, 255, 0.95);
}

QPushButton#NavButton[active="true"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #3a7af8, stop:1 #2457dc);
    border-color: rgba(111, 160, 255, 0.95);
}

QPushButton#PrimaryButton {
    background: #2563eb;
    border: none;
    color: #ffffff;
}

QPushButton#PrimaryButton:hover {
    background: #1d4ed8;
}

QPushButton#DangerButton {
    background: #dc2626;
    border: none;
    color: #ffffff;
}

QPushButton#DangerButton:hover {
    background: #b91c1c;
}

QTreeWidget,
QTreeView {
    background: #ffffff;
    border: 1px solid #d9e2ec;
    border-radius: 16px;
    alternate-background-color: #f8fbff;
    color: #132137;
    outline: 0;
    selection-background-color: #eaf2ff;
    selection-color: #11203a;
}

QTreeWidget::item,
QTreeView::item {
    padding: 8px 4px;
    color: #132137;
    background: transparent;
}

QTreeWidget::item:selected,
QTreeView::item:selected {
    background: #eaf2ff;
    color: #11203a;
}

QTreeWidget::indicator:unchecked,
QTreeView::indicator:unchecked {
    width: 16px;
    height: 16px;
    border: 1px solid #93a5c0;
    border-radius: 4px;
    background: #ffffff;
}

QTreeWidget::indicator:checked,
QTreeView::indicator:checked {
    width: 16px;
    height: 16px;
    border: 1px solid #2563eb;
    border-radius: 4px;
    background: #2563eb;
}

QHeaderView::section {
    background: #f6f9fe;
    color: #32435f;
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid #dbe5f1;
    font-weight: 700;
}

QPlainTextEdit {
    background: #ffffff;
    border: 1px solid #d9e2ec;
    border-radius: 16px;
    padding: 12px;
    color: #132137;
    selection-background-color: #d7e6ff;
}

QComboBox {
    background: #ffffff;
    color: #132137;
    border: 1px solid #d9e2ec;
    border-radius: 12px;
    padding: 9px 12px;
    min-height: 20px;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    color: #132137;
    border: 1px solid #d9e2ec;
    selection-background-color: #eaf2ff;
    selection-color: #11203a;
}

QCheckBox {
    color: #152133;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #93a5c0;
    border-radius: 4px;
    background: #ffffff;
}

QCheckBox::indicator:checked {
    border-color: #2563eb;
    background: #2563eb;
}

QScrollArea {
    background: transparent;
    border: none;
}

QWidget#OverviewScrollHost {
    background: transparent;
}

QWidget#ScrollContent {
    background: transparent;
}

QDialog {
    background: #f8fbff;
}

QDialog QLabel {
    color: #152133;
}

QLabel#ImagePreviewLabel {
    background: #f8fbff;
    border: 1px dashed #d9e2ec;
    border-radius: 16px;
    color: #55657f;
    padding: 18px;
    min-height: 220px;
}

QScrollBar:vertical {
    background: #edf3fb;
    width: 12px;
    margin: 4px 0 4px 0;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #c6d7f4;
    min-height: 36px;
    border-radius: 6px;
}

QScrollBar:horizontal {
    background: #edf3fb;
    height: 12px;
    margin: 0 4px 0 4px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: #c6d7f4;
    min-width: 36px;
    border-radius: 6px;
}

QScrollBar::add-line,
QScrollBar::sub-line,
QScrollBar::add-page,
QScrollBar::sub-page {
    background: transparent;
    border: none;
}
"""

DARK_OVERRIDES = """
QMainWindow {
    background: #0f1728;
}

QWidget#AppRoot {
    background: #0b1322;
}

QLabel {
    color: #edf4ff;
}

QFrame#Sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #10192d, stop:1 #16233e);
    border: 1px solid rgba(78, 105, 151, 0.45);
}

QFrame#ContentCard,
QFrame#InfoCard,
QFrame#OverviewCard,
QFrame#OverviewItemRow {
    background: #121d31;
    border-color: #24344f;
}

QLabel#PageKicker {
    color: #88a3d6;
}

QLabel#PageTitle,
QLabel#DialogTitle {
    color: #edf4ff;
}

QLabel#PageDescription,
QLabel#SidebarCopy,
QLabel#SidebarFooter {
    color: #b5c6e6;
}

QLabel#SummaryLabel {
    background: #17263f;
    color: #d8e7ff;
    border-color: #2d456e;
}

QLabel#TipsLabel {
    background: #5a430d;
    color: #ffe082;
    border-color: #9b7112;
}

QLabel#OverviewSectionTitle,
QLabel#OverviewCardTitle,
QLabel#OverviewItemTitle {
    color: #edf4ff;
}

QLabel#OverviewCardBody {
    background: #10192d;
    color: #c4d4ee;
    border-color: #24344f;
}

QLabel#OverviewItemNote {
    color: #d9e6ff;
}

QLabel#OverviewStatusBadge[severity="ok"] {
    background: rgba(34,197,94,0.18);
    color: #c7f9d9;
}

QLabel#OverviewStatusBadge[severity="issue"] {
    background: rgba(248,113,113,0.18);
    color: #ffd2d2;
}

QPushButton {
    background: #17263f;
    color: #edf4ff;
    border-color: #31486f;
}

QPushButton:hover {
    background: #203152;
}

QPushButton#DialogSecondary {
    background: #17263f;
    color: #edf4ff;
    border-color: #31486f;
}

QTreeWidget,
QTreeView,
QPlainTextEdit,
QDialog {
    background: #10192d;
    alternate-background-color: #16233b;
    color: #edf4ff;
    border-color: #24344f;
    selection-background-color: #1a2a47;
    selection-color: #edf4ff;
}

QTreeWidget::item,
QTreeView::item,
QTreeWidget::item:selected,
QTreeView::item:selected {
    background: transparent;
    color: #edf4ff;
}

QHeaderView::section {
    background: #16233b;
    color: #dfe9ff;
    border-bottom: 1px solid #24344f;
}

QComboBox {
    background: #10192d;
    color: #edf4ff;
    border-color: #24344f;
}

QComboBox QAbstractItemView {
    background: #10192d;
    color: #edf4ff;
    border: 1px solid #24344f;
    selection-background-color: #1a2a47;
    selection-color: #edf4ff;
}

QCheckBox {
    color: #edf4ff;
}

QCheckBox::indicator {
    border-color: #5d7499;
    background: #10192d;
}

QCheckBox::indicator:checked {
    border-color: #4e87ff;
    background: #2563eb;
}

QLabel#ImagePreviewLabel {
    background: #10192d;
    color: #b5c6e6;
    border-color: #2b3d5d;
}

QScrollBar:vertical,
QScrollBar:horizontal {
    background: #0b1322;
}

QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
    background: #2d456e;
}
"""


def format_bytes(value: int | float) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(value or 0)
    index = 0
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    return f"{size:.2f} {units[index]}"


def format_age(age_days: int | None) -> str:
    if age_days is None or age_days < 0:
        return "最近使用时间未知"
    return f"{age_days} 天未修改"


PROTECTED_PREFIXES = [
    Path("/System"),
    Path("/Library"),
    Path("/Applications"),
    Path("/usr"),
    Path("/bin"),
    Path("/sbin"),
    Path("/opt/homebrew"),
]


def build_app_stylesheet(theme_mode: str, system_dark: bool) -> str:
    effective = theme_mode
    if theme_mode == "follow_system":
        effective = "dark" if system_dark else "light"
    if effective == "dark":
        return APP_STYLESHEET + "\n" + DARK_OVERRIDES
    return APP_STYLESHEET


def effective_theme_is_dark(theme_mode: str, system_dark: bool) -> bool:
    if theme_mode == "follow_system":
        return system_dark
    return theme_mode == "dark"


def safe_resolve(path: str) -> Path | None:
    if not path:
        return None
    try:
        return Path(path).expanduser().resolve()
    except Exception:
        return None


def path_under(child: Path | None, root: Path) -> bool:
    if not child:
        return False
    try:
        child.relative_to(root)
        return True
    except ValueError:
        return False


def classify_skipped_path(path: str) -> tuple[str, str, str]:
    resolved = safe_resolve(path)
    if not resolved:
        return ("not_found", "文件路径已变化", "文件可能已经被移动、改名或提前删除，请重新扫描后再试。")
    if not resolved.exists():
        return ("not_found", "文件已不存在", "文件可能已经被移动或删除，请重新扫描后再试。")
    if any(path_under(resolved, prefix) for prefix in PROTECTED_PREFIXES):
        return ("protected", "受保护目录", "该路径位于系统保护范围内，当前版本默认不会直接删除。")
    app_support = Path.home() / "Library" / "Application Support"
    if path_under(resolved, app_support):
        return ("protected", "高风险目录", "该文件位于应用支持目录，当前版本默认会更谨慎地跳过这类路径。")
    if any(
        path_under(resolved, folder)
        for folder in [
            Path.home() / "Desktop",
            Path.home() / "Downloads",
            Path.home() / "Documents",
            Path.home() / "Pictures",
        ]
    ):
        return ("permission", "权限不足或文件被占用", "请先确认已授予桌面、下载、文稿或图片目录权限，并关闭占用该文件的程序后重试。")
    if not resolved.parent.exists():
        return ("not_found", "上级目录已不存在", "文件所在目录已经变化，请重新扫描后再试。")
    if not resolved.is_file():
        return ("not_supported", "目标不是普通文件", "当前版本主要处理普通文件，目录或特殊路径会被跳过。")
    return ("busy", "文件正在使用或系统阻止删除", "请关闭相关应用后重试；如果仍失败，请先在访达中定位确认文件状态。")


def summarize_skip_reasons(skipped_paths: list[str]) -> dict:
    grouped: dict[str, dict] = {}
    for path in skipped_paths:
        code, title, suggestion = classify_skipped_path(path)
        bucket = grouped.setdefault(
            code,
            {
                "title": title,
                "suggestion": suggestion,
                "count": 0,
                "paths": [],
            },
        )
        bucket["count"] += 1
        if len(bucket["paths"]) < 4:
            bucket["paths"].append(path)
    return grouped


def build_cleanup_feedback(result: dict, noun: str) -> dict:
    item = (result.get("results") or [{}])[0]
    deleted_count = int(item.get("deleted_files", 0) or 0)
    reclaimed_bytes = int(item.get("reclaimed_bytes", 0) or 0)
    skipped_paths = list(item.get("skipped_paths") or [])
    skipped_count = len(skipped_paths) + int(item.get("skipped_paths_truncated", 0) or 0)
    deleted_paths = set(item.get("deleted_paths", []))
    reason_groups = summarize_skip_reasons(skipped_paths)

    if deleted_count > 0 and skipped_count == 0:
        mode = "info"
        title = "已完成删除"
        summary = f"删除完成。已删除 {deleted_count} 个{noun}。"
    elif deleted_count > 0:
        mode = "warning"
        title = "部分完成"
        summary = f"部分完成。已删除 {deleted_count} 个{noun}，另有 {skipped_count} 个未处理。"
    else:
        mode = "error"
        title = "删除失败"
        summary = f"未删除任何{noun}。共有 {skipped_count} 个项目未处理。"

    dialog_lines = [
        f"删除{noun}：{deleted_count} 个",
        f"释放空间：{format_bytes(reclaimed_bytes)}",
        f"未处理：{skipped_count} 个",
    ]
    detail_lines = [
        f"{title}",
        "",
        f"删除{noun}：{deleted_count} 个",
        f"释放空间：{format_bytes(reclaimed_bytes)}",
        f"未处理：{skipped_count} 个",
    ]
    repair_section = None
    if reason_groups:
        dialog_lines.append("")
        dialog_lines.append("未处理原因：")
        detail_lines.extend(["", "未处理原因："])
        for group in reason_groups.values():
            dialog_lines.append(f"- {group['title']}: {group['count']} 个")
            detail_lines.append(f"- {group['title']}: {group['count']} 个")
            if group["suggestion"]:
                detail_lines.append(f"  解决建议：{group['suggestion']}")
            for path in group["paths"]:
                detail_lines.append(f"  · {path}")
        if "permission" in reason_groups:
            repair_section = "privacy_files"
    return {
        "summary": summary,
        "title": title,
        "mode": mode,
        "dialog_message": "\n".join(dialog_lines),
        "detail_message": "\n".join(detail_lines),
        "deleted_keys": deleted_paths,
        "repair_section": repair_section,
    }


def detect_system_dark(app: QApplication) -> bool:
    try:
        scheme = app.styleHints().colorScheme()
        return scheme == Qt.ColorScheme.Dark
    except Exception:
        return False


def current_theme_is_dark() -> bool:
    app = QApplication.instance()
    if not app:
        return False
    return bool(app.property("codex_dark_theme"))


def dialog_title_color(role: str) -> str:
    dark = current_theme_is_dark()
    palette = {
        "info": "#edf4ff" if dark else "#102038",
        "warning": "#ffe082" if dark else "#8a5800",
        "error": "#ffd2d2" if dark else "#9f1f1f",
    }
    return palette.get(role, palette["info"])


def _build_message_dialog(
    parent: QWidget,
    title: str,
    message: str,
    *,
    title_color: str,
    primary_text: str = "确定",
    secondary_text: str | None = None,
    action_buttons: list[tuple[str, callable]] | None = None,
) -> tuple[QDialog, QPushButton, QPushButton | None]:
    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setModal(True)
    dialog.setMinimumWidth(540)
    dark = current_theme_is_dark()
    if dark:
        background = "#10192d"
        title_default = "#edf4ff"
        body_background = "#121d31"
        body_color = "#d9e6ff"
        border = "#24344f"
        primary_hover = "#1d4ed8"
        secondary_bg = "#17263f"
        secondary_color = "#edf4ff"
        secondary_hover = "#203152"
    else:
        background = "#f4f8ff"
        title_default = "#102038"
        body_background = "#ffffff"
        body_color = "#25364f"
        border = "#d9e2ec"
        primary_hover = "#1d4ed8"
        secondary_bg = "#ffffff"
        secondary_color = "#182235"
        secondary_hover = "#f7fbff"
    dialog.setStyleSheet(
        f"""
        QDialog {{
            background: {background};
        }}
        QLabel#DialogTitle {{
            color: {title_default};
            font-size: 24px;
            font-weight: 800;
        }}
        QLabel#DialogBody {{
            background: {body_background};
            color: {body_color};
            border: 1px solid {border};
            border-radius: 18px;
            padding: 18px;
            font-size: 15px;
            line-height: 1.55;
        }}
        QPushButton#DialogPrimary {{
            background: #2563eb;
            color: #ffffff;
            border: none;
            border-radius: 12px;
            padding: 11px 20px;
            font-weight: 700;
            min-width: 110px;
        }}
        QPushButton#DialogPrimary:hover {{
            background: {primary_hover};
        }}
        QPushButton#DialogSecondary {{
            background: {secondary_bg};
            color: {secondary_color};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 11px 20px;
            font-weight: 700;
            min-width: 110px;
        }}
        QPushButton#DialogSecondary:hover {{
            background: {secondary_hover};
        }}
        """
    )

    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(22, 22, 22, 22)
    layout.setSpacing(16)

    title_label = QLabel(title)
    title_label.setObjectName("DialogTitle")
    title_label.setStyleSheet(f"color: {title_color};")
    title_label.setWordWrap(True)

    message_label = QLabel(message)
    message_label.setObjectName("DialogBody")
    message_label.setWordWrap(True)

    button_row = QHBoxLayout()
    button_row.setSpacing(12)
    button_row.addStretch(1)

    secondary_button: QPushButton | None = None
    for action_text, action_handler in action_buttons or []:
        action_button = QPushButton(action_text)
        action_button.setObjectName("DialogSecondary")

        def _wrapped_click(checked: bool = False, handler=action_handler, dialog_ref=dialog) -> None:
            try:
                handler()
            finally:
                dialog_ref.accept()

        action_button.clicked.connect(_wrapped_click)
        button_row.addWidget(action_button)

    if secondary_text:
        secondary_button = QPushButton(secondary_text)
        secondary_button.setObjectName("DialogSecondary")
        secondary_button.clicked.connect(dialog.reject)
        button_row.addWidget(secondary_button)

    primary_button = QPushButton(primary_text)
    primary_button.setObjectName("DialogPrimary")
    primary_button.clicked.connect(dialog.accept)
    button_row.addWidget(primary_button)

    layout.addWidget(title_label)
    layout.addWidget(message_label)
    layout.addStretch(1)
    layout.addLayout(button_row)
    dialog.adjustSize()

    return dialog, primary_button, secondary_button


def confirm(parent: QWidget, title: str, message: str) -> bool:
    dialog, _, _ = _build_message_dialog(
        parent,
        title,
        message,
        title_color=dialog_title_color("info"),
        primary_text="继续",
        secondary_text="取消",
    )

    return dialog.exec() == QDialog.DialogCode.Accepted


def confirm_with_actions(
    parent: QWidget,
    title: str,
    message: str,
    *,
    primary_text: str = "继续",
    secondary_text: str = "取消",
    actions: list[tuple[str, callable]] | None = None,
    title_color: str | None = None,
) -> bool:
    dialog, _, _ = _build_message_dialog(
        parent,
        title,
        message,
        title_color=title_color or dialog_title_color("warning"),
        primary_text=primary_text,
        secondary_text=secondary_text,
        action_buttons=actions,
    )
    return dialog.exec() == QDialog.DialogCode.Accepted


def show_error(parent: QWidget, title: str, message: str, *, actions: list[tuple[str, callable]] | None = None) -> None:
    dialog, _, _ = _build_message_dialog(
        parent,
        title,
        message,
        title_color=dialog_title_color("error"),
        primary_text="确定",
        action_buttons=actions,
    )
    dialog.exec()


def show_warning(parent: QWidget, title: str, message: str, *, actions: list[tuple[str, callable]] | None = None) -> None:
    dialog, _, _ = _build_message_dialog(
        parent,
        title,
        message,
        title_color=dialog_title_color("warning"),
        primary_text="确定",
        action_buttons=actions,
    )
    dialog.exec()


def show_info(parent: QWidget, title: str, message: str, *, actions: list[tuple[str, callable]] | None = None) -> None:
    dialog, _, _ = _build_message_dialog(
        parent,
        title,
        message,
        title_color=dialog_title_color("info"),
        primary_text="确定",
        action_buttons=actions,
    )
    dialog.exec()


def permission_dialog_actions(sections: list[str]) -> list[tuple[str, callable]]:
    actions: list[tuple[str, callable]] = []
    if "privacy_files" in sections:
        actions.append(("打开文件夹权限设置", lambda: open_system_settings("privacy_files")))
    if "privacy_automation" in sections:
        actions.append(("打开自动化设置", lambda: open_system_settings("privacy_automation")))
    return actions


def primary_permission_repair_action(sections: list[str]) -> tuple[str, callable] | None:
    actions = permission_dialog_actions(sections)
    if not actions:
        return None
    return actions[0]


def confirm_high_risk_delete(parent: QWidget, title: str, items: list[dict]) -> bool:
    lines = [
        "以下项目被判定为高风险，删除前请再次确认：",
        "",
    ]
    for item in items[:8]:
        name = str(item.get("name") or item.get("path") or "未命名项目")
        reason = str(item.get("reason") or item.get("location_description") or item.get("note") or "高风险项目")
        lines.append(f"- {name}")
        lines.append(f"  原因：{reason}")
    lines.extend(
        [
            "",
            "如果你不确定，请先点“取消”，再用“在访达中显示”确认路径和内容。",
        ]
    )
    dialog, _, _ = _build_message_dialog(
        parent,
        title,
        "\n".join(lines),
        title_color="#9f1f1f",
        primary_text="我已理解，继续删除",
        secondary_text="取消",
    )
    return dialog.exec() == QDialog.DialogCode.Accepted


class ScanProgressDialog(QDialog):
    def __init__(self, parent: QWidget, title: str = "扫描中") -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        dark = current_theme_is_dark()
        background = "#10192d" if dark else "#f4f8ff"
        title_color = "#edf4ff" if dark else "#132137"
        body_color = "#c2d1ea" if dark else "#50627d"
        progress_bg = "#18263f" if dark else "#e6eefc"
        progress_border = "#24344f" if dark else "#d6e1f5"
        progress_text = "#edf4ff" if dark else "#173155"
        self.setStyleSheet(
            f"""
            QDialog {{
                background: {background};
            }}
            QLabel#ProgressTitle {{
                color: {title_color};
                font-size: 24px;
                font-weight: 800;
            }}
            QLabel#ProgressBody {{
                color: {body_color};
                font-size: 14px;
            }}
            QProgressBar {{
                background: {progress_bg};
                border: 1px solid {progress_border};
                border-radius: 12px;
                height: 16px;
                text-align: center;
                color: {progress_text};
                font-weight: 700;
            }}
            QProgressBar::chunk {{
                border-radius: 11px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #2563eb);
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("ProgressTitle")
        self.message_label = QLabel("正在准备，请稍等...")
        self.message_label.setObjectName("ProgressBody")
        self.message_label.setWordWrap(True)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        tip = QLabel("扫描期间窗口会短暂锁定，这是正常现象。")
        tip.setObjectName("ProgressBody")
        tip.setWordWrap(True)

        layout.addWidget(self.title_label)
        layout.addWidget(self.message_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(tip)

    def update_progress(self, value: int, message: str) -> None:
        self.progress_bar.setValue(max(0, min(100, value)))
        self.message_label.setText(message)
        QApplication.processEvents()


def reveal_in_finder(path: str) -> None:
    subprocess.run(["open", "-R", path], check=True)


def open_path(path: str) -> None:
    subprocess.run(["open", path], check=True)


def clean_summary_text(result: dict, title: str) -> str:
    lines = [title, ""]
    for item in result.get("results", []):
        lines.append(f"处理文件数: {item.get('deleted_files', 0)}")
        lines.append(f"释放空间: {format_bytes(item.get('reclaimed_bytes', 0))}")
        skipped = len(item.get("skipped_paths", [])) + int(item.get("skipped_paths_truncated", 0) or 0)
        lines.append(f"跳过文件数: {skipped}")
        if item.get("deleted_paths"):
            lines.append("")
            lines.append("示例路径：")
            for path in item["deleted_paths"][:10]:
                lines.append(f"- {path}")
        if item.get("skipped_paths"):
            lines.append("")
            lines.append("部分跳过路径：")
            for path in item["skipped_paths"][:6]:
                lines.append(f"- {path}")
    return "\n".join(lines)


def localized_finding_name(key: str, fallback: str) -> str:
    mapping = {
        "duplicate_files": "重复文件",
        "stale_large_files": "长期未使用的大文件",
        "installer_files": "安装文件",
        "download_files": "下载文件",
        "largest_files_top10": "大型文件 Top 10",
    }
    return mapping.get(key, fallback)


@dataclass
class NavItem:
    key: str
    title: str
    subtitle: str


class DragCheckTreeWidget(QTreeWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._drag_select_active = False
        self._drag_select_state = Qt.CheckState.Unchecked
        self._drag_last_item: QTreeWidgetItem | None = None
        self._drag_candidate_item: QTreeWidgetItem | None = None
        self._drag_start_pos = QPoint()
        self.setMouseTracking(True)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if (
            event.button() == Qt.MouseButton.LeftButton
            and not (QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier)
        ):
            point = event.position().toPoint()
            item = self.itemAt(point)
            if item and (item.flags() & Qt.ItemFlag.ItemIsUserCheckable):
                column = self.columnAt(point.x())
                if column == 0:
                    self._drag_select_active = True
                    self._drag_last_item = None
                    self._drag_candidate_item = None
                    self._drag_select_state = (
                        Qt.CheckState.Unchecked
                        if item.checkState(0) == Qt.CheckState.Checked
                        else Qt.CheckState.Checked
                    )
                    self.setCurrentItem(item)
                    self._apply_drag_check(item)
                    event.accept()
                    return
                self._drag_candidate_item = item
                self._drag_start_pos = point
            else:
                self._drag_candidate_item = None
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        point = event.position().toPoint()
        if (
            not self._drag_select_active
            and self._drag_candidate_item
            and (point - self._drag_start_pos).manhattanLength() >= 8
        ):
            self._drag_select_active = True
            self._drag_last_item = None
            self._drag_select_state = (
                Qt.CheckState.Unchecked
                if self._drag_candidate_item.checkState(0) == Qt.CheckState.Checked
                else Qt.CheckState.Checked
            )
            self.setCurrentItem(self._drag_candidate_item)
            self._apply_drag_check(self._drag_candidate_item)
        if self._drag_select_active:
            self._auto_scroll(point)
            item = self.itemAt(point)
            if item and (item.flags() & Qt.ItemFlag.ItemIsUserCheckable):
                self.setCurrentItem(item)
                self._apply_drag_check(item)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        self._drag_candidate_item = None
        if self._drag_select_active and event.button() == Qt.MouseButton.LeftButton:
            self._drag_select_active = False
            self._drag_last_item = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        if not self._drag_select_active:
            self._drag_last_item = None
        super().leaveEvent(event)

    def _apply_drag_check(self, item: QTreeWidgetItem) -> None:
        if item is self._drag_last_item:
            return
        self._drag_last_item = item
        item.setCheckState(0, self._drag_select_state)

    def _auto_scroll(self, point: QPoint) -> None:
        margin = 20
        step = max(16, self.verticalScrollBar().singleStep() * 2)
        scrollbar = self.verticalScrollBar()
        if point.y() < margin:
            scrollbar.setValue(scrollbar.value() - step)
        elif point.y() > self.viewport().height() - margin:
            scrollbar.setValue(scrollbar.value() + step)


class OverviewPage(QWidget):
    CARD_POSITIONS = {
        "files": (0, 0, 1, 1),
        "images": (0, 1, 1, 1),
        "space": (1, 0, 1, 1),
        "caches": (1, 1, 1, 1),
        "startup": (2, 0, 1, 1),
        "memory": (2, 1, 1, 1),
        "applications": (3, 0, 1, 2),
    }

    def __init__(self, bridge: CleanerBridge, route_callback, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.bridge = bridge
        self.route_callback = route_callback
        self.settings_manager = get_settings_manager()
        self.cards: list[dict] = []
        self.selected_ids: set[str] = set()
        self.summary_label = QLabel("还没有开始全面检查。")
        self.summary_label.setObjectName("SummaryLabel")
        self.summary_label.setWordWrap(True)
        self.selection_label = QLabel("已勾选 0 项。")
        self.selection_label.setObjectName("PageDescription")
        self.tips_label = QLabel("提示：每张卡片都可以直接勾选；按住左键上下拖动可连续选择；需要看完整列表时点击“打开详情页”。")
        self.tips_label.setObjectName("TipsLabel")
        self.tips_label.setWordWrap(True)
        self.scan_button = QPushButton("开始全面检查")
        self.scan_button.setObjectName("PrimaryButton")
        self.scan_button.clicked.connect(self.refresh_content)
        self.clear_button = QPushButton("清空总览勾选")
        self.clear_button.clicked.connect(self.clear_selection)
        self.execute_button = QPushButton("一键处理已勾选项")
        self.execute_button.setObjectName("DangerButton")
        self.execute_button.clicked.connect(self.execute_selected)
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(16)
        self.cards_layout.setColumnStretch(0, 1)
        self.cards_layout.setColumnStretch(1, 1)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.result_box = QPlainTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setMinimumHeight(180)
        self.cards_host = QWidget()
        self.cards_host.setObjectName("OverviewScrollHost")
        self.cards_host.setLayout(self.cards_layout)
        self.body_host = QWidget()
        self.body_host.setObjectName("OverviewScrollHost")
        self.body_layout = QVBoxLayout(self.body_host)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(16)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        title = QLabel("全面检查")
        title.setObjectName("PageTitle")
        description = QLabel("把所有功能压缩成一页快速总览，只显示更值得你优先处理的几个方向。")
        description.setObjectName("PageDescription")
        description.setWordWrap(True)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)
        toolbar.addWidget(self.scan_button)
        toolbar.addWidget(self.clear_button)
        toolbar.addWidget(self.execute_button)
        toolbar.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        result_card = QFrame()
        result_card.setObjectName("InfoCard")
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(18, 18, 18, 18)
        result_layout.setSpacing(12)
        result_title = QLabel("操作结果")
        result_title.setObjectName("OverviewSectionTitle")
        result_layout.addWidget(result_title)
        self.result_box.setPlainText(
            "使用说明\n\n"
            "1. 点击“开始全面检查”\n"
            "2. 每张卡片会显示最值得优先处理的少量项目\n"
            "3. 你可以直接勾选这些项目\n"
            "4. 点“一键处理已勾选项”后，系统会按功能分批执行"
        )
        result_layout.addWidget(self.result_box)
        self.body_layout.addWidget(self.cards_host)
        self.body_layout.addWidget(result_card)
        scroll.setWidget(self.body_host)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(toolbar)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.selection_label)
        layout.addWidget(self.tips_label)
        layout.addWidget(scroll, 1)

        self._render_cards([])
        self._update_selection_summary()

    def _clear_cards(self) -> None:
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _toggle_item(self, item_id: str, checked: bool) -> None:
        if checked:
            self.selected_ids.add(item_id)
        else:
            self.selected_ids.discard(item_id)
        self._update_selection_summary()

    def _selected_items(self) -> list[dict]:
        return [
            item
            for card in self.cards
            for item in (card.get("items") or [])
            if item.get("id") in self.selected_ids
        ]

    def _update_selection_summary(self) -> None:
        selected = self._selected_items()
        total_bytes = sum(int(item.get("estimated_bytes", 0) or 0) for item in selected)
        self.selection_label.setText(
            f"已勾选 {len(selected)} 项，预计可处理 {format_bytes(total_bytes)} 的文件或内存占用。"
        )
        self.clear_button.setEnabled(bool(self.cards))
        self.execute_button.setEnabled(bool(selected))

    def _overview_feature_keys(self) -> list[str]:
        return ["files", "images", "space", "caches", "startup", "applications"]

    def _build_blocked_cards(self, preflight: dict) -> list[dict]:
        cards = []
        for feature in preflight.get("affected_features", []):
            if not feature.get("blocked"):
                continue
            missing = feature.get("required_missing", [])
            lines = ["缺少必选权限，当前未扫描该模块。"]
            if missing:
                names = "、".join(item.get("name", "未知权限") for item in missing)
                lines.append(f"未授权：{names}")
            lines.append("请先在系统设置中开启权限，然后重启应用后再试。")
            cards.append(
                {
                    "key": feature["key"],
                    "title": feature["name"],
                    "route": feature["key"],
                    "status": "需要授权",
                    "ok": False,
                    "body": "\n".join(lines),
                    "items": [],
                    "actionable_count": 0,
                }
            )
        return cards

    def _run_preflight_checks(self) -> tuple[bool, set[str]]:
        preflight = evaluate_feature_permissions(self._overview_feature_keys())
        if not preflight.get("has_issues"):
            return True, set()

        title, message = build_preflight_message(preflight, overview_mode=True)
        self.result_box.setPlainText(message)
        dialog_actions = permission_dialog_actions(preflight.get("repair_sections", [])) or None
        blocked_keys = {
            feature["key"]
            for feature in preflight.get("affected_features", [])
            if feature.get("blocked")
        }
        proceed = confirm_with_actions(
            self,
            title,
            message,
            primary_text="继续全面检查",
            secondary_text="取消",
            actions=dialog_actions,
        )
        if not proceed:
            self.summary_label.setText("全面检查已取消。")
            return False, blocked_keys
        return True, blocked_keys

    def _safe_reveal(self, item: dict) -> None:
        path = str(item.get("reveal_path") or "")
        if not path:
            show_error(self, "提示", "这个项目暂时没有可在访达中定位的路径。")
            return
        try:
            reveal_in_finder(path)
        except Exception as exc:  # pragma: no cover - runtime UI path
            show_error(self, "定位失败", str(exc))

    def _safe_open(self, item: dict) -> None:
        path = str(item.get("open_path") or "")
        if not path:
            show_error(self, "提示", "这个项目暂时没有可直接打开的路径。")
            return
        try:
            open_path(path)
        except Exception as exc:  # pragma: no cover - runtime UI path
            show_error(self, "打开失败", str(exc))

    def _render_cards(self, cards: list[dict]) -> None:
        self.cards = cards
        self._clear_cards()
        if not cards:
            empty = QFrame()
            empty.setObjectName("InfoCard")
            empty_layout = QVBoxLayout(empty)
            empty_layout.setContentsMargins(18, 18, 18, 18)
            text = QLabel("点击“开始全面检查”后，这里会按功能显示最值得你优先处理的建议。")
            text.setObjectName("PageDescription")
            text.setWordWrap(True)
            empty_layout.addWidget(text)
            self.cards_layout.addWidget(empty, 0, 0, 1, 2)
            return

        for index, card in enumerate(cards):
            row, column, row_span, column_span = self.CARD_POSITIONS.get(card["key"], (index // 2, index % 2, 1, 1))
            frame = QFrame()
            frame.setObjectName("OverviewCard")
            frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            frame.setMaximumWidth(420)
            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(18, 18, 18, 18)
            frame_layout.setSpacing(12)

            head = QHBoxLayout()
            head.setSpacing(10)
            title = QLabel(card["title"])
            title.setObjectName("OverviewCardTitle")
            badge = QLabel(card["status"])
            badge.setObjectName("OverviewStatusBadge")
            badge.setProperty("severity", "ok" if card.get("ok") else "issue")
            head.addWidget(title)
            head.addStretch(1)
            head.addWidget(badge)

            body = QLabel(card["body"])
            body.setObjectName("OverviewCardBody")
            body.setWordWrap(True)

            items_host = QWidget()
            items_layout = QVBoxLayout(items_host)
            items_layout.setContentsMargins(0, 0, 0, 0)
            items_layout.setSpacing(10)
            if card.get("items"):
                for item in card["items"]:
                    item_frame = QFrame()
                    item_frame.setObjectName("OverviewItemRow")
                    item_layout = QHBoxLayout(item_frame)
                    item_layout.setContentsMargins(12, 12, 12, 12)
                    item_layout.setSpacing(12)

                    checkbox = QCheckBox()
                    checkbox.setChecked(item.get("id") in self.selected_ids)
                    checkbox.stateChanged.connect(
                        lambda state, item_id=item.get("id"): self._toggle_item(item_id, state == Qt.CheckState.Checked.value)
                    )

                    text_layout = QVBoxLayout()
                    text_layout.setSpacing(4)
                    item_title = QLabel(str(item.get("name") or "未命名项目"))
                    item_title.setObjectName("OverviewItemTitle")
                    item_title.setWordWrap(True)
                    item_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                    item_meta = QLabel(str(item.get("meta") or "待确认项目"))
                    item_meta.setObjectName("PageDescription")
                    item_meta.setWordWrap(True)
                    item_note = QLabel(str(item.get("note") or "建议手动确认后再处理。"))
                    item_note.setObjectName("OverviewItemNote")
                    item_note.setWordWrap(True)
                    text_layout.addWidget(item_title)
                    text_layout.addWidget(item_meta)
                    text_layout.addWidget(item_note)

                    action_layout = QVBoxLayout()
                    action_layout.setSpacing(8)
                    reveal_button = QPushButton("定位")
                    reveal_button.setFixedWidth(66)
                    reveal_button.setEnabled(bool(item.get("reveal_path")))
                    reveal_button.clicked.connect(lambda checked=False, payload=item: self._safe_reveal(payload))
                    open_button = QPushButton("打开")
                    open_button.setFixedWidth(66)
                    open_button.setEnabled(bool(item.get("open_path")))
                    open_button.clicked.connect(lambda checked=False, payload=item: self._safe_open(payload))
                    action_layout.addWidget(reveal_button)
                    action_layout.addWidget(open_button)
                    action_layout.addStretch(1)

                    item_layout.addWidget(checkbox)
                    item_layout.addLayout(text_layout, 1)
                    item_layout.addLayout(action_layout)
                    items_layout.addWidget(item_frame)
            else:
                empty_item = QLabel(
                    "当前没有需要你手动处理的代表性项目。"
                    if card.get("ok")
                    else "当前没有可直接操作的样本，请点“打开详情页”查看完整列表。"
                )
                empty_item.setObjectName("PageDescription")
                empty_item.setWordWrap(True)
                items_layout.addWidget(empty_item)

            footer = QHBoxLayout()
            footer.addStretch(1)
            button = QPushButton("打开详情页")
            button.clicked.connect(lambda checked=False, route=card["route"]: self.route_callback(route))
            footer.addWidget(button)

            frame_layout.addLayout(head)
            frame_layout.addWidget(body)
            frame_layout.addWidget(items_host)
            frame_layout.addLayout(footer)
            self.cards_layout.addWidget(frame, row, column, row_span, column_span, Qt.AlignmentFlag.AlignTop)
        self._update_selection_summary()

    def clear_selection(self) -> None:
        self.selected_ids.clear()
        self._render_cards(self.cards)

    def execute_selected(self) -> None:
        selected = self._selected_items()
        if not selected:
            show_error(self, "提示", "请先在全面检查页勾选至少一个项目。")
            return
        if self.settings_manager.get("confirm_before_delete", True):
            if not confirm(self, "确认操作", f"即将处理 {len(selected)} 个你勾选的项目，是否继续？"):
                return
        high_risk = [item for item in selected if str(item.get("risk_level") or item.get("payload", {}).get("risk_level") or "") == "高"]
        if high_risk and self.settings_manager.get("confirm_high_risk_delete", True):
            if not confirm_high_risk_delete(self, "高风险删除确认", high_risk):
                return

        self.scan_button.setDisabled(True)
        self.clear_button.setDisabled(True)
        self.execute_button.setDisabled(True)
        self.summary_label.setText("正在分模块处理，请稍候...")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            result = execute_overview_actions(selected, self.bridge)
            lines = [
                "全面检查处理完成",
                "",
                f"成功处理: {result.get('success_count', 0)} 项",
                f"处理失败: {result.get('failed_count', 0)} 项",
                f"释放空间 / 估计回收: {format_bytes(result.get('reclaimed_bytes', 0))}",
            ]
            if result.get("modules"):
                lines.append("")
                lines.append("分模块结果：")
                for module in result["modules"]:
                    lines.append(
                        f"- {module.get('title')}: 成功 {module.get('success_count', 0)} 项，"
                        f"失败 {module.get('failed_count', 0)} 项，"
                        f"释放 {format_bytes(module.get('reclaimed_bytes', 0))}"
                    )
            self.result_box.setPlainText("\n".join(lines))
            dialog_actions = []
            if result.get("failed_count", 0) > 0:
                action_types = {item.get("action_type") for item in selected}
                if {"clean_file", "clean_category"} & action_types:
                    dialog_actions.append(("打开文件夹权限设置", lambda: open_system_settings("privacy_files")))
                if "disable_startup" in action_types:
                    dialog_actions.append(("打开自动化设置", lambda: open_system_settings("privacy_automation")))
            if result.get("failed_count", 0) > 0 and result.get("success_count", 0) == 0:
                show_error(self, "处理失败", "\n".join(lines), actions=dialog_actions or None)
            elif result.get("failed_count", 0) > 0:
                show_warning(self, "部分完成", "\n".join(lines), actions=dialog_actions or None)
            else:
                show_info(self, "已完成处理", "\n".join(lines))
            self.selected_ids.clear()
            self.refresh_content()
        except Exception as exc:  # pragma: no cover - runtime UI path
            show_error(self, "操作失败", str(exc))
        finally:
            QApplication.restoreOverrideCursor()
            self.scan_button.setDisabled(False)
            self.clear_button.setDisabled(False)
            self.execute_button.setDisabled(False)

    def refresh_content(self) -> None:
        proceed, blocked_keys = self._run_preflight_checks()
        if not proceed:
            return
        progress = ScanProgressDialog(self, "全面检查中")
        progress.show()
        self.scan_button.setDisabled(True)
        self.clear_button.setDisabled(True)
        self.execute_button.setDisabled(True)
        self.summary_label.setText("全面检查中，请稍候...")
        progress.update_progress(5, "正在准备全面检查...")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            def _progress_callback(index: int, total: int, label: str) -> None:
                if total <= 0:
                    value = 10
                else:
                    value = 10 + int((index / total) * 80)
                progress.update_progress(value, label)

            result = scan_overview(self.bridge, progress_callback=_progress_callback, skip_keys=blocked_keys)
            progress.update_progress(95, "正在整理检查结果...")
            blocked_cards = self._build_blocked_cards(
                evaluate_feature_permissions(self._overview_feature_keys())
            )
            cards = list(result.get("cards") or [])
            cards.extend(card for card in blocked_cards if card.get("key") not in {entry.get("key") for entry in cards})
            cards.sort(key=lambda card: self.CARD_POSITIONS.get(card["key"], (99, 99, 1, 1)))
            valid_ids = {
                item.get("id")
                for card in cards
                for item in (card.get("items") or [])
            }
            self.selected_ids = {item_id for item_id in self.selected_ids if item_id in valid_ids}
            issue_count = len([card for card in cards if not card.get("ok")])
            self.summary_label.setText(
                "全面检查完成。当前整体状态良好。"
                if issue_count == 0
                else f"全面检查完成。发现 {issue_count} 个更值得优先处理的功能模块。"
            )
            self._render_cards(cards)
            progress.update_progress(100, "全面检查完成。")
        except Exception as exc:  # pragma: no cover - runtime UI path
            self.summary_label.setText(f"全面检查失败：{exc}")
            self._render_cards([])
        finally:
            progress.close()
            QApplication.restoreOverrideCursor()
            self.scan_button.setDisabled(False)
            self.clear_button.setDisabled(False)
            self.execute_button.setDisabled(False)


class InteractivePage(QWidget):
    page_title = ""
    page_description = ""
    scan_button_text = "扫描"
    primary_action_text = ""
    preview_action_text = ""
    selection_empty_text = "扫描后，这里会出现可勾选项目。"
    detail_placeholder = "选择一个项目后，这里会显示详细信息。"
    result_placeholder = "这里会显示扫描结果和操作反馈。"
    primary_action_kind = "neutral"
    scan_progress_title = "扫描中"
    drag_tip_text = "提示：按住左键在勾选列或某一行上上下拖动，可连续选择多项；也可以按住 Shift 选择一整段。"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings_manager = get_settings_manager()
        self.items: list[dict] = []
        self._building_tree = False
        self._last_summary = "还没有扫描。"
        self._last_success_message: str | None = None
        self._last_dialog_mode = "info"
        self._range_anchor_key: str | None = None
        self._pending_range_key: str | None = None
        self._pending_range_state: Qt.CheckState | None = None
        self._repair_action = None
        self._repair_label = "打开修复建议"

        self.scan_button = QPushButton(self.scan_button_text)
        self.scan_button.setObjectName("PrimaryButton")
        self.scan_button.clicked.connect(self.refresh_content)

        self.select_all_button = QPushButton("全选")
        self.select_all_button.clicked.connect(self.select_all_items)

        self.clear_selection_button = QPushButton("清空选择")
        self.clear_selection_button.clicked.connect(self.clear_selected_items)

        self.preview_button = QPushButton(self.preview_action_text) if self.preview_action_text else None
        if self.preview_button:
            self.preview_button.clicked.connect(self.preview_selected)

        self.primary_button = QPushButton(self.primary_action_text) if self.primary_action_text else None
        if self.primary_button:
            self.primary_button.clicked.connect(self.run_primary_action)
            if self.primary_action_kind == "danger":
                self.primary_button.setObjectName("DangerButton")
            else:
                self.primary_button.setObjectName("PrimaryButton")

        self.reveal_button = QPushButton("在访达中显示")
        self.reveal_button.clicked.connect(self.reveal_current)

        self.open_button = QPushButton("尝试打开")
        self.open_button.clicked.connect(self.open_current)

        self.repair_button = QPushButton(self._repair_label)
        self.repair_button.clicked.connect(self.run_repair_action)
        self.repair_button.hide()

        self.summary_label = QLabel(self._last_summary)
        self.summary_label.setObjectName("SummaryLabel")
        self.summary_label.setWordWrap(True)
        self.tips_label = QLabel(self.drag_tip_text)
        self.tips_label.setObjectName("TipsLabel")
        self.tips_label.setWordWrap(True)

        self.tree = DragCheckTreeWidget()
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setUniformRowHeights(False)
        self.tree.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tree.itemPressed.connect(self._handle_item_pressed)
        self.tree.itemChanged.connect(self._handle_item_changed)
        self.tree.currentItemChanged.connect(self._handle_current_item_changed)

        self.detail_box = QPlainTextEdit()
        self.detail_box.setReadOnly(True)
        self.detail_box.setPlainText(self.detail_placeholder)

        self.result_box = QPlainTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setPlainText(self.result_placeholder)

        self.extra_summary_card = self.build_extra_summary_card()
        self._build_ui()
        self._update_action_states()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        title = QLabel(self.page_title)
        title.setObjectName("PageTitle")
        title.setWordWrap(True)
        description = QLabel(self.page_description)
        description.setObjectName("PageDescription")
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        toolbar.addWidget(self.scan_button)
        toolbar.addWidget(self.select_all_button)
        toolbar.addWidget(self.clear_selection_button)
        if self.preview_button:
            toolbar.addWidget(self.preview_button)
        if self.primary_button:
            toolbar.addWidget(self.primary_button)
        toolbar.addStretch(1)
        toolbar.addWidget(self.repair_button)
        toolbar.addWidget(self.reveal_button)
        toolbar.addWidget(self.open_button)
        layout.addLayout(toolbar)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.tips_label)
        if self.extra_summary_card:
            layout.addWidget(self.extra_summary_card)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_list_card())
        splitter.addWidget(self._build_detail_card())
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, 1)

    def _build_list_card(self) -> QWidget:
        card = QFrame()
        card.setObjectName("InfoCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        label = QLabel("可选择项目")
        label.setObjectName("PageDescription")
        layout.addWidget(label)
        layout.addWidget(self.tree, 1)
        return card

    def _build_detail_card(self) -> QWidget:
        card = QWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        detail_card = QFrame()
        detail_card.setObjectName("InfoCard")
        detail_layout = QVBoxLayout(detail_card)
        detail_layout.setContentsMargins(18, 18, 18, 18)
        detail_layout.setSpacing(12)
        detail_label = QLabel("详细信息")
        detail_label.setObjectName("PageDescription")
        detail_layout.addWidget(detail_label)
        detail_layout.addWidget(self.detail_box, 1)

        result_card = QFrame()
        result_card.setObjectName("InfoCard")
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(18, 18, 18, 18)
        result_layout.setSpacing(12)
        result_label = QLabel("操作结果")
        result_label.setObjectName("PageDescription")
        result_layout.addWidget(result_label)
        result_layout.addWidget(self.result_box, 1)

        layout.addWidget(detail_card, 1)
        layout.addWidget(result_card, 1)
        return card

    def refresh_content(self) -> None:
        if not self._run_preflight_checks():
            return
        progress = ScanProgressDialog(self, self.scan_progress_title)
        progress.show()
        self._set_busy(True, "扫描中，请稍候...")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            steps = self.scan_progress_steps()
            if len(steps) < 4:
                steps = [
                    (10, "正在准备扫描..."),
                    (45, "正在扫描，请稍候..."),
                    (82, "正在整理扫描结果..."),
                    (100, "扫描完成。"),
                ]
            progress.update_progress(steps[0][0], steps[0][1])
            progress.update_progress(steps[1][0], steps[1][1])
            self.clear_repair_action()
            payload = self.scan_payload()
            progress.update_progress(steps[2][0], steps[2][1])
            self.items = self.build_items(payload)
            self.after_scan_payload(payload, self.items)
            self.configure_issue_from_scan(payload, self.items)
            self._last_summary = self.scan_summary(payload, self.items)
            self.summary_label.setText(self._last_summary)
            self.result_box.setPlainText(self.scan_details(payload, self.items))
            self.populate_tree()
            progress.update_progress(steps[3][0], steps[3][1])
        except Exception as exc:  # pragma: no cover - runtime UI path
            self.summary_label.setText(f"扫描失败：{exc}")
            self.result_box.setPlainText(f"发生异常：\n{exc}")
            self.set_repair_action("打开系统设置", lambda: open_system_settings("privacy"))
            self.items = []
            self.populate_tree()
        finally:
            progress.close()
            QApplication.restoreOverrideCursor()
            self._set_busy(False)

    def populate_tree(self) -> None:
        self._building_tree = True
        self._range_anchor_key = None
        self._pending_range_key = None
        self._pending_range_state = None
        self.tree.clear()
        self.tree.setHeaderLabels(self.column_headers())
        header = self.tree.header()
        header.setStretchLastSection(False)
        for index in range(len(self.column_headers())):
            mode = QHeaderView.ResizeMode.Stretch if index in {1, len(self.column_headers()) - 1} else QHeaderView.ResizeMode.ResizeToContents
            header.setSectionResizeMode(index, mode)

        if not self.items:
            self.detail_box.setPlainText(self.detail_placeholder)
            self._building_tree = False
            self._update_action_states()
            return

        for data in self.items:
            values = self.row_values(data)
            item = QTreeWidgetItem([""] + values)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            if self.item_is_checkable(data):
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(0, Qt.CheckState.Unchecked)
            item.setData(0, Qt.ItemDataRole.UserRole, data)
            self.tree.addTopLevelItem(item)

        self.tree.setCurrentItem(self.tree.topLevelItem(0))
        self._building_tree = False
        self._update_summary_for_selection()
        self._update_action_states()

    def selected_items(self) -> list[dict]:
        selected: list[dict] = []
        for index in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(index)
            if item.checkState(0) == Qt.CheckState.Checked:
                selected.append(item.data(0, Qt.ItemDataRole.UserRole))
        return selected

    def current_data(self) -> dict | None:
        item = self.tree.currentItem()
        if not item:
            return None
        return item.data(0, Qt.ItemDataRole.UserRole)

    def select_all_items(self) -> None:
        self._building_tree = True
        for index in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(index)
            if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                item.setCheckState(0, Qt.CheckState.Checked)
        self._building_tree = False
        self._update_summary_for_selection()
        self._update_action_states()

    def clear_selected_items(self) -> None:
        self._building_tree = True
        for index in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(index)
            if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                item.setCheckState(0, Qt.CheckState.Unchecked)
        self._building_tree = False
        self._update_summary_for_selection()
        self._update_action_states()

    def preview_selected(self) -> None:
        selected = self.selected_items()
        if not selected:
            show_error(self, "提示", "请先勾选至少一个项目。")
            return
        try:
            result = self.preview_action(selected)
            self.result_box.setPlainText(result)
        except Exception as exc:  # pragma: no cover - runtime UI path
            show_error(self, "预演失败", str(exc))

    def run_primary_action(self) -> None:
        selected = self.selected_items()
        if not selected:
            show_error(self, "提示", "请先勾选至少一个项目。")
            return
        if self.settings_manager.get("confirm_before_delete", True):
            if not confirm(self, "确认操作", self.primary_confirm_message(selected)):
                return
        high_risk_items = self.high_risk_items(selected)
        if high_risk_items and self.settings_manager.get("confirm_high_risk_delete", True):
            if not confirm_high_risk_delete(self, "高风险删除确认", high_risk_items):
                return
        try:
            self._last_success_message = None
            self._last_dialog_mode = "info"
            self.clear_repair_action()
            summary, result, deleted_keys = self.primary_action(selected)
            self.summary_label.setText(summary)
            self.result_box.setPlainText(result)
            if deleted_keys:
                self.after_remove_items(deleted_keys)
            dialog_message = self.success_dialog_message(selected, summary, result)
            if dialog_message:
                title = self.success_dialog_title(selected, summary, result)
                mode = self.success_dialog_mode(selected, summary, result)
                actions = self.success_dialog_actions(selected, summary, result)
                if mode == "error":
                    show_error(self, title, dialog_message, actions=actions)
                elif mode == "warning":
                    show_warning(self, title, dialog_message, actions=actions)
                else:
                    show_info(self, title, dialog_message, actions=actions)
        except Exception as exc:  # pragma: no cover - runtime UI path
            self.set_repair_action("打开系统设置", lambda: open_system_settings("privacy"))
            show_error(self, "操作失败", str(exc), actions=[("打开系统设置", lambda: open_system_settings("privacy"))])

    def after_remove_items(self, deleted_keys: set[str]) -> None:
        self.items = [item for item in self.items if self.item_key(item) not in deleted_keys]
        self.populate_tree()

    def set_repair_action(self, label: str, handler) -> None:
        self._repair_action = handler
        self._repair_label = label
        self.repair_button.setText(label)
        self.repair_button.show()
        self.repair_button.setEnabled(True)

    def clear_repair_action(self) -> None:
        self._repair_action = None
        self._repair_label = "打开修复建议"
        self.repair_button.setText(self._repair_label)
        self.repair_button.hide()
        self.repair_button.setEnabled(False)

    def run_repair_action(self) -> None:
        if not self._repair_action:
            return
        try:
            self._repair_action()
        except Exception as exc:  # pragma: no cover - runtime UI path
            show_error(self, "修复操作失败", str(exc))

    def reveal_current(self) -> None:
        current = self.current_data()
        if not current or not self.reveal_path(current):
            show_error(self, "提示", "当前项目没有可定位的路径。")
            return
        try:
            reveal_in_finder(self.reveal_path(current))
        except Exception as exc:  # pragma: no cover - runtime UI path
            show_error(self, "定位失败", str(exc))

    def open_current(self) -> None:
        current = self.current_data()
        if not current or not self.open_target_path(current):
            show_error(self, "提示", "当前项目没有可打开的路径。")
            return
        try:
            open_path(self.open_target_path(current))
        except Exception as exc:  # pragma: no cover - runtime UI path
            show_error(self, "打开失败", str(exc))

    def _handle_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        if self._building_tree or column != 0:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        key = self.item_key(data)
        if self._pending_range_key == key and self._range_anchor_key and self._range_anchor_key != key:
            self._apply_check_range(self._range_anchor_key, key, self._pending_range_state or item.checkState(0))
            self._pending_range_key = None
            self._pending_range_state = None
        self._range_anchor_key = key
        self._update_summary_for_selection()
        self._update_action_states()
        current = self.current_data()
        if current:
            self.detail_box.setPlainText(self.detail_text(current, self.is_item_checked(current)))

    def _handle_current_item_changed(self, current: QTreeWidgetItem | None, previous: QTreeWidgetItem | None) -> None:
        data = current.data(0, Qt.ItemDataRole.UserRole) if current else None
        if not data:
            self.detail_box.setPlainText(self.detail_placeholder)
        else:
            self.detail_box.setPlainText(self.detail_text(data, self.is_item_checked(data)))
        self._update_action_states()

    def _handle_item_pressed(self, item: QTreeWidgetItem, column: int) -> None:
        if not item or not (item.flags() & Qt.ItemFlag.ItemIsUserCheckable):
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        key = self.item_key(data)
        if QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier and self._range_anchor_key:
            self._pending_range_key = key
            self._pending_range_state = Qt.CheckState.Unchecked if item.checkState(0) == Qt.CheckState.Checked else Qt.CheckState.Checked
        else:
            self._pending_range_key = None
            self._pending_range_state = None
            self._range_anchor_key = key

    def _apply_check_range(self, anchor_key: str, target_key: str, state: Qt.CheckState) -> None:
        anchor_index = -1
        target_index = -1
        for index in range(self.tree.topLevelItemCount()):
            payload = self.tree.topLevelItem(index).data(0, Qt.ItemDataRole.UserRole)
            key = self.item_key(payload)
            if key == anchor_key:
                anchor_index = index
            if key == target_key:
                target_index = index
        if anchor_index < 0 or target_index < 0:
            return
        start, end = sorted((anchor_index, target_index))
        self._building_tree = True
        for index in range(start, end + 1):
            tree_item = self.tree.topLevelItem(index)
            if tree_item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                tree_item.setCheckState(0, state)
        self._building_tree = False

    def _set_busy(self, busy: bool, summary_text: str | None = None) -> None:
        if summary_text:
            self.summary_label.setText(summary_text)
        self.scan_button.setDisabled(busy)
        self.select_all_button.setDisabled(busy)
        self.clear_selection_button.setDisabled(busy)
        if self.preview_button:
            self.preview_button.setDisabled(busy)
        if self.primary_button:
            self.primary_button.setDisabled(busy)
        self.repair_button.setDisabled(busy or not bool(self._repair_action))
        self.reveal_button.setDisabled(busy)
        self.open_button.setDisabled(busy)
        self.tree.setDisabled(busy)

    def _update_summary_for_selection(self) -> None:
        selected = self.selected_items()
        if not self.items:
            self.summary_label.setText("还没有扫描。")
            return
        extra = self.selection_summary(selected)
        if extra:
            self.summary_label.setText(f"{self._last_summary}  {extra}")
        else:
            self.summary_label.setText(self._last_summary)

    def _update_action_states(self) -> None:
        has_items = bool(self.items)
        selected = bool(self.selected_items())
        current = self.current_data()
        self.select_all_button.setEnabled(has_items)
        self.clear_selection_button.setEnabled(has_items)
        if self.preview_button:
            self.preview_button.setEnabled(selected)
        if self.primary_button:
            self.primary_button.setEnabled(selected)
        self.repair_button.setEnabled(bool(self._repair_action))
        self.reveal_button.setEnabled(bool(current and self.reveal_path(current)))
        self.open_button.setEnabled(bool(current and self.open_target_path(current)))

    def item_key(self, item: dict) -> str:
        return str(item.get("key") or item.get("path") or item.get("id") or "")

    def item_is_checkable(self, item: dict) -> bool:
        return True

    def is_item_checked(self, data: dict) -> bool:
        target_key = self.item_key(data)
        for index in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(index)
            payload = item.data(0, Qt.ItemDataRole.UserRole)
            if self.item_key(payload) == target_key:
                if not (item.flags() & Qt.ItemFlag.ItemIsUserCheckable):
                    return False
                return item.checkState(0) == Qt.CheckState.Checked
        return False

    def reveal_path(self, item: dict) -> str:
        return str(item.get("reveal_path") or item.get("path") or "")

    def open_target_path(self, item: dict) -> str:
        return str(item.get("open_path") or item.get("path") or "")

    def column_headers(self) -> list[str]:
        raise NotImplementedError

    def row_values(self, item: dict) -> list[str]:
        raise NotImplementedError

    def scan_payload(self) -> dict:
        raise NotImplementedError

    def build_extra_summary_card(self) -> QWidget | None:
        return None

    def after_scan_payload(self, payload: dict, items: list[dict]) -> None:
        return None

    def build_items(self, payload: dict) -> list[dict]:
        raise NotImplementedError

    def scan_summary(self, payload: dict, items: list[dict]) -> str:
        raise NotImplementedError

    def scan_details(self, payload: dict, items: list[dict]) -> str:
        raise NotImplementedError

    def selection_summary(self, selected: list[dict]) -> str:
        if not selected:
            return "已勾选 0 个。"
        total_size = sum(int(item.get("size", item.get("size_bytes", 0)) or 0) for item in selected)
        return f"已勾选 {len(selected)} 个，共 {format_bytes(total_size)}。"

    def detail_text(self, item: dict, checked: bool) -> str:
        raise NotImplementedError

    def primary_confirm_message(self, selected: list[dict]) -> str:
        return f"即将处理 {len(selected)} 个项目，是否继续？"

    def preview_action(self, selected: list[dict]) -> str:
        raise NotImplementedError

    def primary_action(self, selected: list[dict]) -> tuple[str, str, set[str]]:
        raise NotImplementedError

    def scan_progress_steps(self) -> list[tuple[int, str]]:
        return [
            (10, "正在准备扫描..."),
            (55, "正在扫描，请稍候..."),
            (85, "正在整理扫描结果..."),
            (100, "扫描完成。"),
        ]

    def success_dialog_message(self, selected: list[dict], summary: str, result: str) -> str | None:
        return self._last_success_message

    def success_dialog_title(self, selected: list[dict], summary: str, result: str) -> str:
        return "操作完成"

    def success_dialog_mode(self, selected: list[dict], summary: str, result: str) -> str:
        return self._last_dialog_mode

    def success_dialog_actions(self, selected: list[dict], summary: str, result: str) -> list[tuple[str, callable]] | None:
        if not self._repair_action:
            return None
        return [(self._repair_label, self._repair_action)]

    def high_risk_items(self, selected: list[dict]) -> list[dict]:
        return []

    def permission_feature_keys(self) -> list[str]:
        return []

    def _run_preflight_checks(self) -> bool:
        feature_keys = self.permission_feature_keys()
        if not feature_keys:
            return True

        preflight = evaluate_feature_permissions(feature_keys)
        if not preflight.get("has_issues"):
            return True

        self.clear_repair_action()
        repair_action = primary_permission_repair_action(preflight.get("repair_sections", []))
        if repair_action:
            label, handler = repair_action
            self.set_repair_action(label, handler)

        title, message = build_preflight_message(preflight)
        self.result_box.setPlainText(message)
        dialog_actions = permission_dialog_actions(preflight.get("repair_sections", [])) or None
        if preflight.get("blocked"):
            self.summary_label.setText(f"{self.page_title}暂时无法开始扫描。")
            show_error(self, title, message, actions=dialog_actions)
            return False

        proceed = confirm_with_actions(
            self,
            title,
            message,
            primary_text="继续扫描已授权目录",
            secondary_text="取消",
            actions=dialog_actions,
        )
        if not proceed:
            self.summary_label.setText("扫描已取消。")
            return False
        return True

    def configure_issue_from_scan(self, payload: dict, items: list[dict]) -> None:
        return None

    def scan_warning(self, payload: dict, items: list[dict]) -> tuple[str, str, list[tuple[str, callable]] | None] | None:
        return None


class FileCleaningPage(InteractivePage):
    page_title = "文件清理"
    page_description = "扫描并整理候选文件、安装文件、下载文件和大型文件。"
    scan_button_text = "扫描文件"
    primary_action_text = "删除所选文件"
    preview_action_text = ""
    selection_empty_text = "扫描后，这里会显示候选文件、安装文件、下载文件和大型文件。"
    detail_placeholder = "扫描后，点击某个文件，就会在这里看到分组、路径、大小和说明。"
    result_placeholder = "使用说明\n\n1. 点击“扫描文件”\n2. 在列表里勾选要处理的文件\n3. 直接删除前，建议先在访达中定位确认\n4. 可以按住左键在勾选列或某一行上上下拖动，连续选择一段文件"
    primary_action_kind = "danger"
    scan_progress_title = "扫描文件中"

    def __init__(self, bridge: CleanerBridge, parent: QWidget | None = None) -> None:
        self.bridge = bridge
        super().__init__(parent)

    def build_extra_summary_card(self) -> QWidget | None:
        card = QFrame()
        card.setObjectName("InfoCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        title = QLabel("基础清理")
        title.setObjectName("PageDescription")
        copy = QLabel("这里会单独显示用户缓存、用户日志和废纸篓的体积，方便你确认基础清理值得不值得做。")
        copy.setObjectName("PageDescription")
        copy.setWordWrap(True)
        self.base_cleanup_label = QLabel("还没有扫描基础清理分类。")
        self.base_cleanup_label.setObjectName("SummaryLabel")
        self.base_cleanup_label.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(copy)
        layout.addWidget(self.base_cleanup_label)
        return card

    def column_headers(self) -> list[str]:
        return ["选择", "文件名", "大小", "分组", "说明"]

    def row_values(self, item: dict) -> list[str]:
        return [
            item["name"],
            format_bytes(item["size"]),
            item["group"],
            item["note"],
        ]

    def scan_payload(self) -> dict:
        return self.bridge.scan(["user_cache", "user_logs", "trash"])

    def permission_feature_keys(self) -> list[str]:
        return ["files"]

    def build_items(self, payload: dict) -> list[dict]:
        items: list[dict] = []
        for finding in payload.get("findings", []):
            group_name = localized_finding_name(finding.get("key", ""), finding.get("name", "候选文件"))
            for file in finding.get("files", []):
                path = file["path"]
                items.append(
                    {
                        "key": path,
                        "name": Path(path).name or path,
                        "path": path,
                        "reveal_path": path,
                        "open_path": path,
                        "size": int(file.get("size", 0) or 0),
                        "age_days": file.get("age_days"),
                        "group": group_name,
                        "note": file.get("note") or "可手动确认是否需要",
                    }
                )
        for file in payload.get("large_files", {}).get("files", []):
            path = file["path"]
            items.append(
                {
                    "key": path,
                    "name": Path(path).name or path,
                    "path": path,
                    "reveal_path": path,
                    "open_path": path,
                    "size": int(file.get("size", 0) or 0),
                    "age_days": file.get("age_days"),
                    "group": "大型文件 Top 10",
                    "note": file.get("note") or "按大小排名进入前 10",
                }
            )
        items.sort(key=lambda item: (-item["size"], item["path"]))
        return items

    def after_scan_payload(self, payload: dict, items: list[dict]) -> None:
        categories = {entry.get("key"): entry for entry in payload.get("categories", [])}
        cache = categories.get("user_cache") or {}
        logs = categories.get("user_logs") or {}
        trash = categories.get("trash") or {}
        self.base_cleanup_label.setText(
            " | ".join(
                [
                    f"用户缓存：{format_bytes(cache.get('total_bytes', 0))}（{int(cache.get('file_count', 0) or 0)} 个）",
                    f"用户日志：{format_bytes(logs.get('total_bytes', 0))}（{int(logs.get('file_count', 0) or 0)} 个）",
                    f"废纸篓：{format_bytes(trash.get('total_bytes', 0))}（{int(trash.get('file_count', 0) or 0)} 个）",
                ]
            )
        )

    def scan_summary(self, payload: dict, items: list[dict]) -> str:
        finding_count = len(payload.get("findings", []))
        categories = {entry.get("key"): entry for entry in payload.get("categories", [])}
        return (
            f"共发现 {len(items)} 个可查看项目，"
            f"其中候选分组 {finding_count} 组，"
            f"大型文件 {payload.get('large_files', {}).get('file_count', 0)} 个；"
            f"用户日志 {format_bytes((categories.get('user_logs') or {}).get('total_bytes', 0))}。"
        )

    def scan_details(self, payload: dict, items: list[dict]) -> str:
        lines = [
            "文件清理扫描摘要",
            "",
            f"基础清理总空间: {format_bytes(payload.get('grand_total_bytes', 0))}",
            f"手动确认总空间: {format_bytes(payload.get('grand_total_candidate_bytes', 0))}",
            f"当前展示项目数: {len(items)}",
            "",
            "分组：",
        ]
        for category in payload.get("categories", []):
            lines.append(
                f"- {category.get('name')}: {category.get('file_count', 0)} 个，{format_bytes(category.get('total_bytes', 0))}"
            )
        for finding in payload.get("findings", []):
            lines.append(
                f"- {localized_finding_name(finding.get('key', ''), finding.get('name', '候选文件'))}: "
                f"{finding.get('file_count', 0)} 个，{format_bytes(finding.get('total_bytes', 0))}"
            )
        if payload.get("large_files", {}).get("file_count"):
            lines.append(
                f"- 大型文件 Top 10: {payload['large_files'].get('file_count', 0)} 个，"
                f"{format_bytes(payload['large_files'].get('total_bytes', 0))}"
            )
        return "\n".join(lines)

    def detail_text(self, item: dict, checked: bool) -> str:
        return "\n".join(
            [
                f"文件名: {item['name']}",
                f"分组: {item['group']}",
                f"状态: {'已勾选' if checked else '未勾选'}",
                f"大小: {format_bytes(item['size'])}",
                f"使用情况: {format_age(item.get('age_days'))}",
                f"说明: {item['note']}",
                "",
                "完整路径:",
                item["path"],
            ]
        )

    def preview_action(self, selected: list[dict]) -> str:
        result = self.bridge.clean_files([item["path"] for item in selected], dry_run=True)
        return clean_summary_text(result, "预演所选文件")

    def primary_confirm_message(self, selected: list[dict]) -> str:
        return f"即将删除 {len(selected)} 个你勾选的文件，是否继续？"

    def primary_action(self, selected: list[dict]) -> tuple[str, str, set[str]]:
        result = self.bridge.clean_files([item["path"] for item in selected], dry_run=False)
        feedback = build_cleanup_feedback(result, "文件")
        self._last_success_message = feedback["dialog_message"]
        self._last_dialog_mode = feedback["mode"]
        if feedback.get("repair_section") == "privacy_files":
            self.set_repair_action("打开文件夹权限设置", lambda: open_system_settings("privacy_files"))
        return feedback["summary"], feedback["detail_message"], feedback["deleted_keys"]

    def success_dialog_title(self, selected: list[dict], summary: str, result: str) -> str:
        if self._last_dialog_mode == "error":
            return "删除失败"
        if self._last_dialog_mode == "warning":
            return "部分完成"
        return "已完成删除"

    def scan_progress_steps(self) -> list[tuple[int, str]]:
        return [
            (10, "正在准备文件清理扫描..."),
            (55, "正在扫描候选文件、安装文件和大型文件..."),
            (85, "正在整理文件结果..."),
            (100, "文件扫描完成。"),
        ]


class AppCachesPage(InteractivePage):
    page_title = "软件缓存"
    page_description = "扫描常见软件的缓存文件，并优先展示体积较大的项目。"
    scan_button_text = "扫描软件缓存"
    primary_action_text = "删除缓存文件"
    preview_action_text = ""
    detail_placeholder = "扫描后，点击某个缓存文件，就会在这里看到所属应用、大小和缓存说明。"
    result_placeholder = "这里会显示软件缓存扫描摘要和删除反馈。"
    primary_action_kind = "danger"
    scan_progress_title = "扫描软件缓存中"

    def __init__(self, bridge: CleanerBridge, parent: QWidget | None = None) -> None:
        self.bridge = bridge
        super().__init__(parent)

    def column_headers(self) -> list[str]:
        return ["选择", "文件名", "大小", "所属应用", "缓存说明"]

    def row_values(self, item: dict) -> list[str]:
        return [
            item["name"],
            format_bytes(item["size"]),
            item["group"],
            item["note"],
        ]

    def scan_payload(self) -> dict:
        return self.bridge.scan_app_caches([])

    def permission_feature_keys(self) -> list[str]:
        return ["caches"]

    def build_items(self, payload: dict) -> list[dict]:
        items = []
        for file in payload.get("files", []):
            path = file["path"]
            items.append(
                {
                    "key": path,
                    "name": Path(path).name or path,
                    "path": path,
                    "reveal_path": path,
                    "open_path": path,
                    "size": int(file.get("size", 0) or 0),
                    "age_days": file.get("age_days"),
                    "group": file.get("group", "未知应用"),
                    "note": file.get("note") or "缓存文件",
                }
            )
        items.sort(key=lambda item: (-item["size"], item["group"], item["path"]))
        return items

    def scan_summary(self, payload: dict, items: list[dict]) -> str:
        return f"共发现 {payload.get('total_file_count', 0)} 个缓存文件，当前展示 {len(items)} 个大型缓存文件。"

    def scan_details(self, payload: dict, items: list[dict]) -> str:
        lines = [
            "软件缓存扫描摘要",
            "",
            f"总文件数: {payload.get('total_file_count', 0)}",
            f"总空间: {format_bytes(payload.get('total_bytes', 0))}",
            f"当前展示: {len(items)} 个大型缓存文件",
            "",
            "应用分组：",
        ]
        for item in payload.get("categories", []):
            lines.append(f"- {item.get('name')}: {item.get('file_count', 0)} 个，{format_bytes(item.get('total_bytes', 0))}")
        return "\n".join(lines)

    def detail_text(self, item: dict, checked: bool) -> str:
        return "\n".join(
            [
                f"所属应用: {item['group']}",
                f"文件名: {item['name']}",
                f"状态: {'已勾选' if checked else '未勾选'}",
                f"大小: {format_bytes(item['size'])}",
                f"使用情况: {format_age(item.get('age_days'))}",
                f"说明: {item['note']}",
                "",
                "完整路径:",
                item["path"],
            ]
        )

    def preview_action(self, selected: list[dict]) -> str:
        result = self.bridge.clean_files([item["path"] for item in selected], dry_run=True)
        return clean_summary_text(result, "预演缓存文件")

    def primary_confirm_message(self, selected: list[dict]) -> str:
        return f"即将删除 {len(selected)} 个缓存文件，是否继续？"

    def primary_action(self, selected: list[dict]) -> tuple[str, str, set[str]]:
        result = self.bridge.clean_files([item["path"] for item in selected], dry_run=False)
        feedback = build_cleanup_feedback(result, "缓存文件")
        self._last_success_message = feedback["dialog_message"]
        self._last_dialog_mode = feedback["mode"]
        if feedback.get("repair_section") == "privacy_files":
            self.set_repair_action("打开文件夹权限设置", lambda: open_system_settings("privacy_files"))
        return feedback["summary"], feedback["detail_message"], feedback["deleted_keys"]

    def success_dialog_title(self, selected: list[dict], summary: str, result: str) -> str:
        if self._last_dialog_mode == "error":
            return "删除失败"
        if self._last_dialog_mode == "warning":
            return "部分完成"
        return "已完成删除"

    def scan_progress_steps(self) -> list[tuple[int, str]]:
        return [
            (10, "正在准备软件缓存扫描..."),
            (55, "正在扫描常见应用缓存目录..."),
            (85, "正在整理软件缓存结果..."),
            (100, "软件缓存扫描完成。"),
        ]


class ImageManagementPage(InteractivePage):
    page_title = "图片管理"
    page_description = "优先整理截图，同时处理下载图片、照片图库中的图片、相似图片、完全重复图片，以及大图 / 长期未使用图片。"
    scan_button_text = "扫描图片"
    primary_action_text = "删除所选图片"
    preview_action_text = ""
    detail_placeholder = "扫描后，点击某张图片，就会在这里显示预览、路径、大小、分辨率和分类说明。"
    result_placeholder = "这里会显示图片管理扫描摘要和删除结果。"
    primary_action_kind = "danger"
    scan_progress_title = "扫描图片中"

    CATEGORY_ORDER = {
        "截图": 0,
        "下载图片": 1,
        "相似图片": 2,
        "完全重复图片": 3,
        "大图 / 旧图": 4,
    }

    def __init__(self, bridge: CleanerBridge, parent: QWidget | None = None) -> None:
        self.bridge = bridge
        self.preview_label: QLabel | None = None
        super().__init__(parent)

    def _build_detail_card(self) -> QWidget:
        card = QWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        detail_card = QFrame()
        detail_card.setObjectName("InfoCard")
        detail_layout = QVBoxLayout(detail_card)
        detail_layout.setContentsMargins(18, 18, 18, 18)
        detail_layout.setSpacing(12)

        detail_label = QLabel("图片详情")
        detail_label.setObjectName("PageDescription")
        detail_layout.addWidget(detail_label)

        self.preview_label = QLabel("选择图片后，这里会显示预览。")
        self.preview_label.setObjectName("ImagePreviewLabel")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setWordWrap(True)
        detail_layout.addWidget(self.preview_label)
        detail_layout.addWidget(self.detail_box, 1)

        result_card = QFrame()
        result_card.setObjectName("InfoCard")
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(18, 18, 18, 18)
        result_layout.setSpacing(12)
        result_label = QLabel("操作结果")
        result_label.setObjectName("PageDescription")
        result_layout.addWidget(result_label)
        result_layout.addWidget(self.result_box, 1)

        layout.addWidget(detail_card, 1)
        layout.addWidget(result_card, 1)
        return card

    def column_headers(self) -> list[str]:
        return ["选择", "图片名", "大小", "分类", "说明"]

    def row_values(self, item: dict) -> list[str]:
        return [
            item["name"],
            format_bytes(item["size_bytes"]),
            item["category"],
            item["reason"],
        ]

    def scan_payload(self) -> dict:
        return scan_image_library(["desktop", "downloads", "pictures"])

    def permission_feature_keys(self) -> list[str]:
        return ["images"]

    def build_items(self, payload: dict) -> list[dict]:
        sections = [
            payload.get("screenshots", {}).get("items", []),
            payload.get("downloads", {}).get("items", []),
            payload.get("similar", {}).get("items", []),
            payload.get("duplicates", {}).get("items", []),
            payload.get("large_old", {}).get("items", []),
        ]
        items = [item for section in sections for item in section]
        items.sort(
            key=lambda item: (
                self.CATEGORY_ORDER.get(item.get("category", ""), 9),
                -int(item.get("size_bytes", 0) or 0),
                item.get("path", ""),
            )
        )
        return items

    def scan_summary(self, payload: dict, items: list[dict]) -> str:
        return (
            f"共扫描到 {payload.get('scanned_image_count', 0)} 张图片，"
            f"当前展示 {len(items)} 个图片项目；截图 {payload.get('screenshots', {}).get('total_count', 0)} 张。"
        )

    def scan_details(self, payload: dict, items: list[dict]) -> str:
        lines = [
            "图片管理扫描摘要",
            "",
            f"总图片数: {payload.get('scanned_image_count', 0)}",
            f"总空间: {format_bytes(payload.get('total_bytes', 0))}",
            f"当前展示: {len(items)} 个图片项目",
            "提示: 同一张图片可能同时出现在多个分类里。",
            "分类统计：",
            f"- 截图: {payload.get('screenshots', {}).get('total_count', 0)} 张",
            f"- 下载图片: {payload.get('downloads', {}).get('total_count', 0)} 张",
            f"- 相似图片: {payload.get('similar', {}).get('group_count', 0)} 组，共 {payload.get('similar', {}).get('total_count', 0)} 张",
            f"- 完全重复图片: {payload.get('duplicates', {}).get('group_count', 0)} 组，共 {payload.get('duplicates', {}).get('total_count', 0)} 张",
            f"- 大图 / 旧图: {payload.get('large_old', {}).get('total_count', 0)} 张",
            "",
            "扫描目录：",
        ]
        for root in payload.get("roots", []):
            if not root.get("exists", True):
                status = "目录不存在"
            elif not root.get("accessible", False):
                status = "没有访问权限"
            else:
                status = "已授权"
            lines.append(
                f"- {root.get('name')}: {root.get('image_count', 0)} 张，"
                f"{format_bytes(root.get('total_bytes', 0))} | {status}"
            )
            if root.get("error"):
                lines.append(f"  错误: {root.get('error')}")
        return "\n".join(lines)

    def detail_text(self, item: dict, checked: bool) -> str:
        return "\n".join(
            [
                f"分类: {item['category']}",
                f"文件名: {item['name']}",
                f"来源目录: {item.get('root_name', '未知')}",
                f"状态: {'已勾选' if checked else '未勾选'}",
                f"大小: {format_bytes(item['size_bytes'])}",
                f"分辨率: {item.get('dimensions', '未知')}",
                f"使用情况: {format_age(item.get('age_days'))}",
                f"组别: {item['group_label']}" if item.get("group_label") else "",
                f"说明: {item.get('reason', '可手动确认是否需要')}",
                "",
                "完整路径:",
                item["path"],
            ]
        )

    def preview_action(self, selected: list[dict]) -> str:
        result = self.bridge.clean_files([item["path"] for item in selected], dry_run=True)
        return clean_summary_text(result, "预演所选图片")

    def primary_confirm_message(self, selected: list[dict]) -> str:
        return f"即将删除 {len(selected)} 张图片，是否继续？"

    def primary_action(self, selected: list[dict]) -> tuple[str, str, set[str]]:
        result = self.bridge.clean_files([item["path"] for item in selected], dry_run=False)
        feedback = build_cleanup_feedback(result, "图片")
        self._last_success_message = feedback["dialog_message"]
        self._last_dialog_mode = feedback["mode"]
        if feedback.get("repair_section") == "privacy_files":
            self.set_repair_action("打开文件夹权限设置", lambda: open_system_settings("privacy_files"))
        return feedback["summary"], feedback["detail_message"], feedback["deleted_keys"]

    def success_dialog_title(self, selected: list[dict], summary: str, result: str) -> str:
        if self._last_dialog_mode == "error":
            return "删除失败"
        if self._last_dialog_mode == "warning":
            return "部分完成"
        return "已完成删除"

    def _update_preview(self, item: dict | None) -> None:
        if not self.preview_label:
            return
        if not item:
            self.preview_label.clear()
            self.preview_label.setText("选择图片后，这里会显示预览。")
            return
        try:
            preview_path = create_image_preview(item["path"], 480)
            pixmap = QPixmap(str(preview_path))
            if pixmap.isNull():
                raise ValueError("预览图加载失败")
            self.preview_label.setPixmap(
                pixmap.scaled(
                    440,
                    260,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.preview_label.setText("")
        except Exception:
            self.preview_label.clear()
            self.preview_label.setText("当前图片暂时无法预览，但仍然可以在访达中定位或直接打开。")

    def _handle_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        super()._handle_item_changed(item, column)
        self._update_preview(self.current_data())

    def _handle_current_item_changed(self, current: QTreeWidgetItem | None, previous: QTreeWidgetItem | None) -> None:
        super()._handle_current_item_changed(current, previous)
        self._update_preview(current.data(0, Qt.ItemDataRole.UserRole) if current else None)

    def scan_progress_steps(self) -> list[tuple[int, str]]:
        return [
            (10, "正在准备图片管理扫描..."),
            (52, "正在扫描截图、下载图片和相似图片候选..."),
            (86, "正在整理图片结果与预览索引..."),
            (100, "图片扫描完成。"),
        ]


class DiskAnalysisPage(InteractivePage):
    page_title = "磁盘空间"
    page_description = "先看目录占用，再处理最占空间的大文件。"
    scan_button_text = "扫描磁盘空间"
    primary_action_text = "删除所选大文件"
    preview_action_text = ""
    detail_placeholder = "扫描后，点击某个大文件，就会在这里显示来源目录、大小和完整路径。"
    result_placeholder = "这里会显示磁盘空间扫描摘要和大文件处理结果。"
    primary_action_kind = "danger"
    scan_progress_title = "扫描磁盘空间中"

    def __init__(self, bridge: CleanerBridge, parent: QWidget | None = None) -> None:
        self.bridge = bridge
        super().__init__(parent)

    def column_headers(self) -> list[str]:
        return ["选择", "文件名", "大小", "来源", "说明"]

    def row_values(self, item: dict) -> list[str]:
        return [
            item["name"],
            format_bytes(item["size_bytes"]),
            item["source_root"],
            item["note"],
        ]

    def scan_payload(self) -> dict:
        return scan_disk_usage(["desktop", "downloads", "documents", "library"])

    def permission_feature_keys(self) -> list[str]:
        return ["space"]

    def build_items(self, payload: dict) -> list[dict]:
        items = []
        for item in payload.get("large_files", []):
            items.append(
                {
                    "key": item["path"],
                    "name": item["name"],
                    "path": item["path"],
                    "reveal_path": item["path"],
                    "open_path": item["path"],
                    "size_bytes": int(item.get("size_bytes", 0) or 0),
                    "source_root": item.get("source_root", ""),
                    "note": "磁盘空间分析里最占空间的大文件",
                }
            )
        items.sort(key=lambda item: (-item["size_bytes"], item["path"]))
        return items

    def scan_summary(self, payload: dict, items: list[dict]) -> str:
        return (
            f"共统计 {payload.get('root_count', 0)} 个根目录，"
            f"总空间 {format_bytes(payload.get('total_bytes', 0))}；"
            f"当前展示 {len(items)} 个大文件。"
        )

    def scan_details(self, payload: dict, items: list[dict]) -> str:
        lines = [
            "磁盘空间扫描摘要",
            "",
            f"根目录数: {payload.get('root_count', 0)}",
            f"总文件数: {payload.get('total_file_count', 0)}",
            f"总空间: {format_bytes(payload.get('total_bytes', 0))}",
            "",
            "目录概览：",
        ]
        for root in payload.get("roots", []):
            if not root.get("exists", True):
                status = "目录不存在"
            elif not root.get("accessible", False):
                status = "没有访问权限"
            else:
                status = "已授权"
            lines.append(
                f"- {root.get('name')}: {format_bytes(root.get('total_bytes', 0))}，{root.get('file_count', 0)} 个文件 | {status}"
            )
            for child in (root.get("children") or [])[:5]:
                lines.append(f"  · {child.get('name')}: {format_bytes(child.get('size_bytes', 0))} | {child.get('kind')}")
            if root.get("error"):
                lines.append(f"  错误: {root.get('error')}")
        return "\n".join(lines)

    def detail_text(self, item: dict, checked: bool) -> str:
        return "\n".join(
            [
                f"文件名: {item['name']}",
                f"来源目录: {item['source_root']}",
                f"状态: {'已勾选' if checked else '未勾选'}",
                f"大小: {format_bytes(item['size_bytes'])}",
                f"说明: {item['note']}",
                "",
                "完整路径:",
                item["path"],
            ]
        )

    def preview_action(self, selected: list[dict]) -> str:
        result = self.bridge.clean_files([item["path"] for item in selected], dry_run=True)
        return clean_summary_text(result, "预演所选大文件")

    def primary_confirm_message(self, selected: list[dict]) -> str:
        return f"即将删除 {len(selected)} 个大文件，是否继续？"

    def primary_action(self, selected: list[dict]) -> tuple[str, str, set[str]]:
        result = self.bridge.clean_files([item["path"] for item in selected], dry_run=False)
        feedback = build_cleanup_feedback(result, "大文件")
        self._last_success_message = feedback["dialog_message"]
        self._last_dialog_mode = feedback["mode"]
        if feedback.get("repair_section") == "privacy_files":
            self.set_repair_action("打开文件夹权限设置", lambda: open_system_settings("privacy_files"))
        return feedback["summary"], feedback["detail_message"], feedback["deleted_keys"]

    def success_dialog_title(self, selected: list[dict], summary: str, result: str) -> str:
        if self._last_dialog_mode == "error":
            return "删除失败"
        if self._last_dialog_mode == "warning":
            return "部分完成"
        return "已完成删除"

    def scan_progress_steps(self) -> list[tuple[int, str]]:
        return [
            (10, "正在准备磁盘空间分析..."),
            (58, "正在统计目录占用和大文件..."),
            (86, "正在整理空间分析结果..."),
            (100, "磁盘空间扫描完成。"),
        ]


class StartupPage(InteractivePage):
    page_title = "开机启动"
    page_description = "扫描登录项和后台项目，支持查看详情并关闭所选项目。"
    scan_button_text = "扫描开机启动项"
    primary_action_text = "关闭所选启动项"
    detail_placeholder = "扫描后，点击某个启动项，就会在这里显示路径、类型和估计影响。"
    result_placeholder = "这里会显示开机启动扫描摘要和关闭结果。"
    primary_action_kind = "danger"
    scan_progress_title = "扫描开机启动项中"

    def column_headers(self) -> list[str]:
        return ["选择", "名称", "类型", "估计影响", "目标路径"]

    def row_values(self, item: dict) -> list[str]:
        return [
            item["name"],
            item["kind_label"],
            item["impact_level"],
            item["target_display"],
        ]

    def scan_payload(self) -> dict:
        return scan_startup_items(["login_items", "launch_agents"])

    def build_items(self, payload: dict) -> list[dict]:
        items = []
        for item in payload.get("items", []):
            action_path = item.get("action_path") or item.get("path") or item.get("plist_path") or ""
            items.append(
                {
                    "key": item["id"],
                    "id": item["id"],
                    "name": item["name"],
                    "kind": item["kind"],
                    "kind_label": "登录项" if item.get("kind") == "login_item" else "后台项目",
                    "impact_level": item.get("impact_level", "低"),
                    "impact_reason": item.get("impact_reason", "未提供"),
                    "group": item.get("group", ""),
                    "action_path": action_path,
                    "path": item.get("path", ""),
                    "plist_path": item.get("plist_path", ""),
                    "label": item.get("label", ""),
                    "hidden": bool(item.get("hidden")),
                    "run_at_load": bool(item.get("run_at_load")),
                    "start_interval": int(item.get("start_interval", 0) or 0),
                    "watch_paths": list(item.get("watch_paths") or []),
                    "target_display": action_path or "未解析到路径",
                    "raw_item": item,
                }
            )
        return items

    def scan_summary(self, payload: dict, items: list[dict]) -> str:
        return f"共发现 {payload.get('total_count', 0)} 个启动项，其中高影响 {payload.get('high_impact_count', 0)} 个。"

    def scan_details(self, payload: dict, items: list[dict]) -> str:
        lines = [
            "开机启动扫描摘要",
            "",
            f"总项目数: {payload.get('total_count', 0)}",
            f"高影响项目: {payload.get('high_impact_count', 0)}",
            "",
            "分组：",
        ]
        for group in payload.get("groups", []):
            lines.append(f"- {group.get('name')}: {group.get('count', 0)} 个，高影响 {group.get('high_impact_count', 0)} 个")
        return "\n".join(lines)

    def detail_text(self, item: dict, checked: bool) -> str:
        return "\n".join(
            [
                f"名称: {item['name']}",
                f"类型: {item['kind_label']}",
                f"来源分组: {item['group']}",
                f"状态: {'已勾选' if checked else '未勾选'}",
                f"估计影响: {item['impact_level']}",
                f"判断依据: {item['impact_reason']}",
                f"隐藏启动: {'是' if item['hidden'] else '否'}",
                f"RunAtLoad: {'是' if item['run_at_load'] else '否'}",
                f"StartInterval: {item['start_interval']} 秒" if item["start_interval"] else "StartInterval: 无",
                f"WatchPaths: {' | '.join(item['watch_paths'])}" if item["watch_paths"] else "WatchPaths: 无",
                f"配置文件: {item['plist_path']}" if item["plist_path"] else "",
                "",
                f"目标路径: {item['target_display']}",
            ]
        )

    def selection_summary(self, selected: list[dict]) -> str:
        if not selected:
            return "已勾选 0 个。"
        high_count = sum(1 for item in selected if item.get("impact_level") == "高")
        return f"已勾选 {len(selected)} 个，其中高影响 {high_count} 个。"

    def reveal_path(self, item: dict) -> str:
        return item.get("action_path") or item.get("plist_path") or ""

    def open_target_path(self, item: dict) -> str:
        return item.get("action_path") or item.get("plist_path") or ""

    def preview_action(self, selected: list[dict]) -> str:
        return "开机启动页没有预演模式。请确认后直接关闭所选项目。"

    def permission_feature_keys(self) -> list[str]:
        return ["startup"]

    def primary_confirm_message(self, selected: list[dict]) -> str:
        return f"即将关闭 {len(selected)} 个开机启动项，是否继续？"

    def primary_action(self, selected: list[dict]) -> tuple[str, str, set[str]]:
        result = disable_startup_items([item["raw_item"] for item in selected])
        lines = [
            "关闭开机启动项结果",
            "",
            f"成功: {result.get('disabled_count', 0)}",
            f"失败: {result.get('failed_count', 0)}",
            "",
        ]
        for item in result.get("results", []):
            lines.append(f"- {item.get('name')}: {'成功' if item.get('success') else '失败'} | {item.get('message')}")
        disabled_count = result.get('disabled_count', 0)
        failed_count = result.get('failed_count', 0)
        if disabled_count > 0 and failed_count == 0:
            summary = f"关闭完成。成功 {disabled_count} 个。"
        elif disabled_count > 0:
            summary = f"部分完成。成功 {disabled_count} 个，失败 {failed_count} 个。"
        else:
            summary = f"关闭失败。失败 {failed_count} 个。"
        failed_results = [item for item in result.get("results", []) if not item.get("success")]
        message_lines = [
            "已完成关闭。",
            "",
            f"成功关闭：{disabled_count} 个",
            f"失败项目：{failed_count} 个",
        ]
        if failed_results:
            message_lines.extend(["", "失败原因："])
            for item in failed_results[:4]:
                message_lines.append(f"- {item.get('name')}: {item.get('message')}")
        if failed_results and any("权限" in str(item.get("message")) or "不允许删除" in str(item.get("message")) for item in failed_results):
            self.set_repair_action("打开文件夹权限设置", lambda: open_system_settings("privacy_files"))
        self._last_success_message = "\n".join(message_lines)
        self._last_dialog_mode = "error" if disabled_count == 0 and failed_count > 0 else ("warning" if failed_count > 0 else "info")
        if failed_results and any("自动化" in str(item.get("message")) or "System Events" in str(item.get("message")) for item in failed_results):
            self.set_repair_action("打开自动化设置", lambda: open_system_settings("privacy_automation"))
        deleted_keys = {item.get("id") for item in result.get("results", []) if item.get("success")}
        return summary, "\n".join(lines), deleted_keys

    def success_dialog_title(self, selected: list[dict], summary: str, result: str) -> str:
        if self._last_dialog_mode == "error":
            return "关闭失败"
        if self._last_dialog_mode == "warning":
            return "部分完成"
        return "已完成关闭"

    def success_dialog_actions(self, selected: list[dict], summary: str, result: str) -> list[tuple[str, callable]] | None:
        actions = super().success_dialog_actions(selected, summary, result) or []
        if self._repair_action and not actions:
            actions.append((self._repair_label, self._repair_action))
        return actions or None

    def scan_progress_steps(self) -> list[tuple[int, str]]:
        return [
            (10, "正在准备启动项扫描..."),
            (55, "正在读取登录项和后台项目..."),
            (85, "正在整理启动项结果..."),
            (100, "开机启动扫描完成。"),
        ]


class MemoryPage(InteractivePage):
    page_title = "内存管理"
    page_description = "扫描当前用户中占用较高的进程，给出风险说明，并允许你选择性结束。"
    scan_button_text = "扫描内存进程"
    primary_action_text = "结束所选进程"
    detail_placeholder = "扫描后，点击某个进程，就会在这里显示 PID、内存、CPU、风险说明和命令行。"
    result_placeholder = "这里会显示内存扫描摘要和结束进程结果。"
    primary_action_kind = "danger"
    scan_progress_title = "扫描内存进程中"

    def column_headers(self) -> list[str]:
        return ["选择", "进程名", "内存", "CPU", "后台", "风险"]

    def row_values(self, item: dict) -> list[str]:
        return [
            item["name"],
            format_bytes(item["memory_bytes"]),
            f"{float(item['cpu_percent']):.1f}%",
            "是" if item["is_background"] else "否",
            item["risk_level"],
        ]

    def scan_payload(self) -> dict:
        return scan_memory_processes(20)

    def build_items(self, payload: dict) -> list[dict]:
        return list(payload.get("items") or [])

    def item_is_checkable(self, item: dict) -> bool:
        return bool(item.get("can_terminate"))

    def scan_summary(self, payload: dict, items: list[dict]) -> str:
        return (
            f"当前展示 {payload.get('visible_count', 0)} 个高占用进程，"
            f"总占用 {format_bytes(payload.get('visible_memory_bytes', 0))}，"
            f"其中低风险 {payload.get('low_risk_count', 0)} 个。"
        )

    def scan_details(self, payload: dict, items: list[dict]) -> str:
        lines = [
            "内存管理扫描摘要",
            "",
            f"当前用户进程总数: {payload.get('current_user_process_count', 0)}",
            f"可管理候选进程: {payload.get('total_candidate_count', 0)}",
            f"当前展示: {payload.get('visible_count', 0)} 个",
            f"展示中的总内存占用: {format_bytes(payload.get('visible_memory_bytes', 0))}",
            f"低风险进程: {payload.get('low_risk_count', 0)}",
            f"后台进程: {payload.get('background_count', 0)}",
            f"高内存进程: {payload.get('high_memory_count', 0)}",
        ]
        return "\n".join(lines)

    def detail_text(self, item: dict, checked: bool) -> str:
        return "\n".join(
            [
                f"进程名: {item['name']}",
                f"应用家族: {item['family']}",
                f"PID: {item['pid']}",
                f"父进程 PID: {item['ppid']}",
                f"状态: {'已勾选' if checked else '未勾选'}",
                f"内存占用: {format_bytes(item['memory_bytes'])}",
                f"CPU 占用: {float(item['cpu_percent']):.1f}%",
                f"后台进程: {'是' if item['is_background'] else '否'}",
                f"风险等级: {item['risk_level']}",
                f"可结束: {'是' if item.get('can_terminate') else '否'}",
                f"说明: {item['recommendation']}",
                f"应用路径: {item['app_path']}" if item.get("app_path") else "应用路径: 未解析到 .app",
                "",
                "命令行:",
                item["command"],
            ]
        )

    def selection_summary(self, selected: list[dict]) -> str:
        if not selected:
            return "已勾选 0 个。"
        total_memory = sum(int(item.get("memory_bytes") or 0) for item in selected)
        low_risk_count = sum(1 for item in selected if item.get("risk_level") == "低")
        return f"已勾选 {len(selected)} 个，估计占用 {format_bytes(total_memory)}，其中低风险 {low_risk_count} 个。"

    def reveal_path(self, item: dict) -> str:
        return str(item.get("app_path") or "")

    def open_target_path(self, item: dict) -> str:
        return str(item.get("app_path") or "")

    def preview_action(self, selected: list[dict]) -> str:
        return "内存管理页没有预演模式。建议先看风险说明，再决定是否结束进程。"

    def primary_confirm_message(self, selected: list[dict]) -> str:
        total_memory = sum(int(item.get("memory_bytes") or 0) for item in selected)
        return f"即将结束 {len(selected)} 个进程，估计涉及 {format_bytes(total_memory)} 内存占用，是否继续？"

    def primary_action(self, selected: list[dict]) -> tuple[str, str, set[str]]:
        result = terminate_processes(selected)
        lines = [
            "结束进程结果",
            "",
            f"成功: {result.get('terminated_count', 0)}",
            f"失败: {result.get('failed_count', 0)}",
            f"估计释放内存: {format_bytes(result.get('reclaimed_bytes_estimate', 0))}",
            "",
        ]
        for item in result.get("results", []):
            lines.append(f"- {item.get('name')} (PID {item.get('pid')}): {'成功' if item.get('success') else '失败'} | {item.get('message')}")
        success_count = result.get("terminated_count", 0)
        failed_count = result.get("failed_count", 0)
        if success_count > 0 and failed_count == 0:
            summary = f"结束完成。成功 {success_count} 个，估计释放 {format_bytes(result.get('reclaimed_bytes_estimate', 0))}。"
        elif success_count > 0:
            summary = (
                f"部分完成。成功 {success_count} 个，失败 {failed_count} 个，"
                f"估计释放 {format_bytes(result.get('reclaimed_bytes_estimate', 0))}。"
            )
        else:
            summary = f"结束失败。失败 {failed_count} 个。"
        failed_results = [item for item in result.get("results", []) if not item.get("success")]
        message_lines = [
            "内存管理操作完成。",
            "",
            f"成功结束：{success_count} 个",
            f"失败项目：{failed_count} 个",
            f"估计释放内存：{format_bytes(result.get('reclaimed_bytes_estimate', 0))}",
        ]
        if failed_results:
            message_lines.extend(["", "失败原因："])
            for item in failed_results[:4]:
                message_lines.append(f"- {item.get('name')}: {item.get('message')}")
        self._last_success_message = "\n".join(message_lines)
        self._last_dialog_mode = "error" if success_count == 0 and failed_count > 0 else ("warning" if failed_count > 0 else "info")
        deleted_keys = {f"process::{item.get('pid')}" for item in result.get("results", []) if item.get("success")}
        return summary, "\n".join(lines), deleted_keys

    def success_dialog_title(self, selected: list[dict], summary: str, result: str) -> str:
        if self._last_dialog_mode == "error":
            return "结束失败"
        if self._last_dialog_mode == "warning":
            return "部分完成"
        return "已完成内存整理"

    def scan_progress_steps(self) -> list[tuple[int, str]]:
        return [
            (10, "正在准备内存分析..."),
            (55, "正在扫描高占用进程与风险等级..."),
            (85, "正在整理内存管理结果..."),
            (100, "内存扫描完成。"),
        ]


class ApplicationsPage(InteractivePage):
    page_title = "应用程序"
    page_description = "扫描应用残留目录，支持在访达中确认后再删除。"
    scan_button_text = "扫描应用残留"
    primary_action_text = "删除所选残留"
    detail_placeholder = "扫描后，点击某个残留项目，就会在这里显示路径、风险等级和判断依据。"
    result_placeholder = "这里会显示应用残留扫描摘要和删除结果。"
    primary_action_kind = "danger"
    scan_progress_title = "扫描应用残留中"

    def column_headers(self) -> list[str]:
        return ["选择", "名称", "大小", "目录类型", "风险", "判断依据"]

    def row_values(self, item: dict) -> list[str]:
        return [
            item["name"],
            format_bytes(item["size_bytes"]),
            item["location_type"],
            item["risk_level"],
            item["reason"],
        ]

    def scan_payload(self) -> dict:
        return scan_app_residuals()

    def permission_feature_keys(self) -> list[str]:
        return ["applications"]

    def build_items(self, payload: dict) -> list[dict]:
        items = []
        for item in payload.get("items", []):
            items.append(
                {
                    "key": item["path"],
                    "name": item["name"],
                    "path": item["path"],
                    "reveal_path": item["path"],
                    "open_path": item["path"],
                    "size_bytes": int(item.get("size_bytes", 0) or 0),
                    "location_type": item.get("location_type", ""),
                    "risk_level": item.get("risk_level", "低"),
                    "reason": item.get("reason", ""),
                    "location_description": item.get("location_description", ""),
                    "identifier": item.get("identifier", ""),
                    "is_directory": bool(item.get("is_directory")),
                    "raw_item": item,
                }
            )
        items.sort(key=lambda item: ({"高": 0, "中": 1, "低": 2}.get(item["risk_level"], 3), -item["size_bytes"], item["path"]))
        return items

    def scan_summary(self, payload: dict, items: list[dict]) -> str:
        return f"共发现 {payload.get('total_count', 0)} 个疑似残留，高风险 {payload.get('high_risk_count', 0)} 个。"

    def scan_details(self, payload: dict, items: list[dict]) -> str:
        lines = [
            "应用残留扫描摘要",
            "",
            f"总项目数: {payload.get('total_count', 0)}",
            f"总空间: {format_bytes(payload.get('total_bytes', 0))}",
            f"高风险项目: {payload.get('high_risk_count', 0)}",
            "",
            "应用分组：",
        ]
        for group in payload.get("groups", [])[:12]:
            lines.append(f"- {group.get('name')}: {group.get('count', 0)} 个，{format_bytes(group.get('total_bytes', 0))}")
        return "\n".join(lines)

    def detail_text(self, item: dict, checked: bool) -> str:
        return "\n".join(
            [
                f"名称: {item['name']}",
                f"标识符: {item['identifier']}",
                f"状态: {'已勾选' if checked else '未勾选'}",
                f"大小: {format_bytes(item['size_bytes'])}",
                f"目录类型: {item['location_type']}",
                f"风险等级: {item['risk_level']}",
                f"判断依据: {item['reason']}",
                f"目录说明: {item['location_description']}",
                f"项目类型: {'目录' if item['is_directory'] else '文件'}",
                "",
                "完整路径:",
                item["path"],
            ]
        )

    def selection_summary(self, selected: list[dict]) -> str:
        if not selected:
            return "已勾选 0 个。"
        total_size = sum(item["size_bytes"] for item in selected)
        high_count = sum(1 for item in selected if item["risk_level"] == "高")
        return f"已勾选 {len(selected)} 个，共 {format_bytes(total_size)}，其中高风险 {high_count} 个。"

    def high_risk_items(self, selected: list[dict]) -> list[dict]:
        return [item for item in selected if item.get("risk_level") == "高"]

    def preview_action(self, selected: list[dict]) -> str:
        return "应用残留页没有预演模式。建议先在访达中确认路径，再删除。"

    def primary_confirm_message(self, selected: list[dict]) -> str:
        return f"即将删除 {len(selected)} 个应用残留，是否继续？"

    def primary_action(self, selected: list[dict]) -> tuple[str, str, set[str]]:
        result = clean_app_residuals([item["raw_item"] for item in selected])
        lines = [
            "删除应用残留结果",
            "",
            f"成功: {result.get('deleted_count', 0)}",
            f"失败: {result.get('failed_count', 0)}",
            f"释放空间: {format_bytes(result.get('reclaimed_bytes', 0))}",
            "",
        ]
        for item in result.get("results", []):
            lines.append(f"- {item.get('name')}: {'成功' if item.get('success') else '失败'} | {item.get('message')}")
        deleted_count = int(result.get("deleted_count", 0) or 0)
        failed_count = int(result.get("failed_count", 0) or 0)
        if deleted_count > 0 and failed_count == 0:
            summary = f"删除完成。成功 {deleted_count} 个。"
        elif deleted_count > 0:
            summary = f"部分完成。成功 {deleted_count} 个，失败 {failed_count} 个。"
        else:
            summary = f"删除失败。失败 {failed_count} 个。"
        failed_results = [item for item in result.get("results", []) if not item.get("success")]
        message_lines = [
            "应用残留处理完成。",
            "",
            f"删除残留：{deleted_count} 个",
            f"释放空间：{format_bytes(result.get('reclaimed_bytes', 0))}",
            f"失败项目：{failed_count} 个",
        ]
        if failed_results:
            message_lines.extend(["", "失败原因："])
            for item in failed_results[:4]:
                message_lines.append(f"- {item.get('name')}: {item.get('message')}")
        self._last_success_message = "\n".join(message_lines)
        self._last_dialog_mode = "error" if deleted_count == 0 and failed_count > 0 else ("warning" if failed_count > 0 else "info")
        deleted_keys = {item.get("path") for item in result.get("results", []) if item.get("success")}
        return summary, "\n".join(lines), deleted_keys

    def success_dialog_title(self, selected: list[dict], summary: str, result: str) -> str:
        if self._last_dialog_mode == "error":
            return "删除失败"
        if self._last_dialog_mode == "warning":
            return "部分完成"
        return "已完成删除"

    def scan_progress_steps(self) -> list[tuple[int, str]]:
        return [
            (10, "正在准备应用残留扫描..."),
            (55, "正在扫描残留目录与风险项..."),
            (85, "正在整理应用残留结果..."),
            (100, "应用残留扫描完成。"),
        ]


class SettingsPage(QWidget):
    def __init__(self, apply_theme_callback, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings_manager = get_settings_manager()
        self.apply_theme_callback = apply_theme_callback
        self.summary_label = QLabel("正在读取设置与权限状态...")
        self.summary_label.setObjectName("SummaryLabel")
        self.summary_label.setWordWrap(True)
        self.runtime_box = QPlainTextEdit()
        self.runtime_box.setReadOnly(True)
        self.permissions_box = QPlainTextEdit()
        self.permissions_box.setReadOnly(True)
        self.theme_combo = QComboBox()
        for key, label in THEME_OPTIONS.items():
            self.theme_combo.addItem(label, key)
        self.confirm_delete_checkbox = QCheckBox("执行处理前总是先确认一次")
        self.confirm_high_risk_checkbox = QCheckBox("高风险删除必须二次确认")
        self._build_ui()
        self._load_settings()
        self.refresh_status()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        title = QLabel("设置")
        title.setObjectName("PageTitle")
        description = QLabel("查看版本与运行环境、检测权限状态，并调整外观和安全确认行为。")
        description.setObjectName("PageDescription")
        description.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.summary_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        body.setObjectName("ScrollContent")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(16)

        version_card = QFrame()
        version_card.setObjectName("InfoCard")
        version_layout = QVBoxLayout(version_card)
        version_layout.setContentsMargins(18, 18, 18, 18)
        version_layout.setSpacing(12)
        version_title = QLabel("版本与运行环境")
        version_title.setObjectName("PageDescription")
        version_layout.addWidget(version_title)
        version_layout.addWidget(self.runtime_box)

        permissions_card = QFrame()
        permissions_card.setObjectName("InfoCard")
        permissions_layout = QVBoxLayout(permissions_card)
        permissions_layout.setContentsMargins(18, 18, 18, 18)
        permissions_layout.setSpacing(12)
        permissions_title = QLabel("权限状态与修复")
        permissions_title.setObjectName("PageDescription")
        permissions_layout.addWidget(permissions_title)
        permissions_layout.addWidget(self.permissions_box)
        permission_buttons = QHBoxLayout()
        permission_buttons.setSpacing(10)
        open_files_button = QPushButton("打开文件夹权限设置")
        open_files_button.clicked.connect(lambda: open_system_settings("privacy_files"))
        open_automation_button = QPushButton("打开自动化设置")
        open_automation_button.clicked.connect(lambda: open_system_settings("privacy_automation"))
        permission_buttons.addWidget(open_files_button)
        permission_buttons.addWidget(open_automation_button)
        permission_buttons.addStretch(1)
        permissions_layout.addLayout(permission_buttons)

        appearance_card = QFrame()
        appearance_card.setObjectName("InfoCard")
        appearance_layout = QVBoxLayout(appearance_card)
        appearance_layout.setContentsMargins(18, 18, 18, 18)
        appearance_layout.setSpacing(12)
        appearance_title = QLabel("外观与安全确认")
        appearance_title.setObjectName("PageDescription")
        appearance_layout.addWidget(appearance_title)
        theme_row = QHBoxLayout()
        theme_row.setSpacing(10)
        theme_label = QLabel("界面配色：")
        theme_label.setObjectName("PageDescription")
        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch(1)
        appearance_layout.addLayout(theme_row)
        appearance_layout.addWidget(self.confirm_delete_checkbox)
        appearance_layout.addWidget(self.confirm_high_risk_checkbox)

        help_card = QFrame()
        help_card.setObjectName("InfoCard")
        help_layout = QVBoxLayout(help_card)
        help_layout.setContentsMargins(18, 18, 18, 18)
        help_layout.setSpacing(12)
        help_title = QLabel("帮助与定位")
        help_title.setObjectName("PageDescription")
        help_layout.addWidget(help_title)
        help_copy = QLabel(
            "如果某个功能扫描不完整或删除失败，先来这里看权限状态；"
            "权限修改通常需要重启应用后才会稳定生效；"
            "如果需要进一步排查，可以定位底层核心或设置文件。"
        )
        help_copy.setObjectName("PageDescription")
        help_copy.setWordWrap(True)
        help_layout.addWidget(help_copy)
        help_buttons = QHBoxLayout()
        help_buttons.setSpacing(10)
        reveal_core_button = QPushButton("定位底层核心")
        reveal_core_button.clicked.connect(self.reveal_core_binary)
        reveal_settings_button = QPushButton("定位设置文件")
        reveal_settings_button.clicked.connect(self.reveal_settings_file)
        open_general_button = QPushButton("打开系统设置")
        open_general_button.clicked.connect(lambda: open_system_settings("general"))
        help_buttons.addWidget(reveal_core_button)
        help_buttons.addWidget(reveal_settings_button)
        help_buttons.addWidget(open_general_button)
        help_buttons.addStretch(1)
        help_layout.addLayout(help_buttons)

        body_layout.addWidget(version_card)
        body_layout.addWidget(permissions_card)
        body_layout.addWidget(appearance_card)
        body_layout.addWidget(help_card)
        body_layout.addStretch(1)
        scroll.setWidget(body)
        layout.addWidget(scroll, 1)

        self.theme_combo.currentIndexChanged.connect(self._theme_changed)
        self.confirm_delete_checkbox.toggled.connect(self._confirm_delete_changed)
        self.confirm_high_risk_checkbox.toggled.connect(self._confirm_high_risk_changed)

    def _load_settings(self) -> None:
        theme_mode = self.settings_manager.get("theme_mode", "follow_system")
        index = max(0, self.theme_combo.findData(theme_mode))
        self.theme_combo.blockSignals(True)
        self.theme_combo.setCurrentIndex(index)
        self.theme_combo.blockSignals(False)
        self.confirm_delete_checkbox.blockSignals(True)
        self.confirm_delete_checkbox.setChecked(bool(self.settings_manager.get("confirm_before_delete", True)))
        self.confirm_delete_checkbox.blockSignals(False)
        self.confirm_high_risk_checkbox.blockSignals(True)
        self.confirm_high_risk_checkbox.setChecked(bool(self.settings_manager.get("confirm_high_risk_delete", True)))
        self.confirm_high_risk_checkbox.blockSignals(False)

    def refresh_status(self) -> None:
        runtime = self.settings_manager.runtime_info()
        permissions = self.settings_manager.scan_folder_permissions()
        self.summary_label.setText(
            f"当前版本 {runtime['app_version']} | "
            f"已授权目录 {permissions['granted_count']} 项，未授权 {permissions['denied_count']} 项。"
            " 如果你刚修改过系统权限，请重启应用后再回来查看。"
        )
        self.runtime_box.setPlainText(
            "\n".join(
                [
                    f"应用名称: {runtime['app_name']}",
                    f"版本号: {runtime['app_version']}",
                    f"运行方式: {'打包版应用' if runtime['packaged'] else '源码运行'}",
                    f"系统版本: {runtime['system_version']}",
                    f"硬件架构: {runtime['architecture']}",
                    f"Python 版本: {runtime['python_version']}",
                    f"底层核心: {runtime['core_binary']}",
                    f"底层核心状态: {'已就绪' if runtime['core_binary_exists'] else '缺失'}",
                    f"设置文件: {runtime['settings_path']}",
                ]
            )
        )
        lines = [
            "权限检查结果",
            "",
        ]
        for item in permissions["items"]:
            lines.append(f"- {item['name']}: {item['status_label']} | {item['path']}")
            if item.get("error"):
                lines.append(f"  说明: {item['error']}")
        lines.extend(
            [
                "",
                "说明：权限状态不是热更新的；如果你刚在系统设置里修改过权限，请重启应用后再看这里。",
                "",
                "自动化权限提示：关闭“登录项”依赖系统的自动化控制。",
                "如果开机启动页提示没有权限，请点击上方“打开自动化设置”。",
                "",
                "功能与目录依赖：",
            ]
        )
        for feature in feature_directory_map():
            lines.append("")
            lines.append(f"[{feature['name']}]")
            for requirement in feature["requirements"]:
                level = "必选" if requirement["required"] else "可选"
                if requirement["kind"] == "automation":
                    lines.append(f"- {level} · {requirement['name']}（自动化权限）")
                else:
                    lines.append(f"- {level} · {requirement['name']} | {requirement['path']}")
        self.permissions_box.setPlainText("\n".join(lines))

    def _theme_changed(self) -> None:
        theme_mode = str(self.theme_combo.currentData())
        self.settings_manager.set("theme_mode", theme_mode)
        self.apply_theme_callback()

    def _confirm_delete_changed(self, checked: bool) -> None:
        self.settings_manager.set("confirm_before_delete", bool(checked))

    def _confirm_high_risk_changed(self, checked: bool) -> None:
        self.settings_manager.set("confirm_high_risk_delete", bool(checked))

    def reveal_core_binary(self) -> None:
        runtime = self.settings_manager.runtime_info()
        core_path = runtime["core_binary"]
        if Path(core_path).exists():
            reveal_in_finder(core_path)
        else:
            show_error(self, "定位失败", "当前没有找到底层核心二进制。")

    def reveal_settings_file(self) -> None:
        settings_path = self.settings_manager.runtime_info()["settings_path"]
        path_obj = Path(settings_path)
        if path_obj.exists():
            reveal_in_finder(str(path_obj))
        else:
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            open_path(str(path_obj.parent))


class CleanerDesktopWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.bridge = CleanerBridge()
        self.settings_manager = get_settings_manager()
        self.setWindowTitle("macOS Cleaner Desktop")
        self.resize(1400, 900)
        self.setMinimumSize(1100, 720)

        root = QWidget()
        root.setObjectName("AppRoot")
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(18)

        root_layout.addWidget(self._build_sidebar(), 0)
        root_layout.addWidget(self._build_content(), 1)

        self.setCentralWidget(root)
        self.apply_theme()
        self.switch_page("overview")

    def _build_sidebar(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Sidebar")
        frame.setMinimumWidth(260)
        frame.setMaximumWidth(320)
        frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(18)

        title = QLabel("macOS Cleaner")
        title.setObjectName("BrandTitle")
        layout.addWidget(title)

        self.nav_buttons: dict[str, QPushButton] = {}
        for item in [
            NavItem("overview", "全面检查", "把所有功能压成一页快速总览"),
            NavItem("files", "文件清理", "候选文件、安装文件、下载文件、大型文件"),
            NavItem("images", "图片管理", "截图、下载图片、相似图、重复图、大图旧图"),
            NavItem("space", "磁盘空间", "目录占用概览和大文件处理"),
            NavItem("caches", "软件缓存", "浏览器与常见应用缓存"),
            NavItem("startup", "开机启动", "登录项和后台项目"),
            NavItem("memory", "内存管理", "高占用进程与风险判断"),
            NavItem("applications", "应用程序", "应用残留和高风险目录"),
            NavItem("settings", "设置", "版本、权限、外观与安全确认"),
        ]:
            button = QPushButton(f"{item.title}\n{item.subtitle}")
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, key=item.key: self.switch_page(key))
            self.nav_buttons[item.key] = button
            layout.addWidget(button)

        layout.addStretch(1)
        footer = QLabel("浏览器版：python3 python/gui.py")
        footer.setObjectName("SidebarFooter")
        footer.setWordWrap(True)
        layout.addWidget(footer)
        return frame

    def _build_content(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("ContentCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        self.stack = QStackedWidget()
        self.pages = {
            "overview": OverviewPage(self.bridge, self.switch_page),
            "files": FileCleaningPage(self.bridge),
            "images": ImageManagementPage(self.bridge),
            "space": DiskAnalysisPage(self.bridge),
            "caches": AppCachesPage(self.bridge),
            "startup": StartupPage(),
            "memory": MemoryPage(),
            "applications": ApplicationsPage(),
            "settings": SettingsPage(self.apply_theme),
        }

        for page in self.pages.values():
            page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.stack.addWidget(page)

        layout.addWidget(self.stack)
        return frame

    def switch_page(self, key: str) -> None:
        self.stack.setCurrentWidget(self.pages[key])
        for button_key, button in self.nav_buttons.items():
            active = button_key == key
            button.setChecked(active)
            button.setProperty("active", "true" if active else "false")
            button.style().unpolish(button)
            button.style().polish(button)

    def apply_theme(self) -> None:
        app = QApplication.instance()
        system_dark = detect_system_dark(app) if app else False
        theme_mode = str(self.settings_manager.get("theme_mode", "follow_system"))
        if app:
            app.setProperty("codex_dark_theme", effective_theme_is_dark(theme_mode, system_dark))
        self.setStyleSheet(build_app_stylesheet(theme_mode, system_dark))
