from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


HOME = Path.home()


@dataclass(frozen=True)
class PermissionRequirement:
    key: str
    name: str
    kind: str
    required: bool
    section: str
    path: str = ""
    description: str = ""


@dataclass(frozen=True)
class FeaturePermissionSpec:
    key: str
    name: str
    requirements: tuple[PermissionRequirement, ...]


def _directory_requirement(
    key: str,
    name: str,
    path: Path,
    *,
    required: bool,
    section: str = "privacy_files",
    description: str = "",
) -> PermissionRequirement:
    return PermissionRequirement(
        key=key,
        name=name,
        kind="directory",
        path=str(path),
        required=required,
        section=section,
        description=description,
    )


def _automation_requirement(
    key: str,
    name: str,
    *,
    required: bool,
    section: str = "privacy_automation",
    description: str = "",
) -> PermissionRequirement:
    return PermissionRequirement(
        key=key,
        name=name,
        kind="automation",
        required=required,
        section=section,
        description=description,
    )


FEATURE_SPECS: dict[str, FeaturePermissionSpec] = {
    "files": FeaturePermissionSpec(
        key="files",
        name="文件清理",
        requirements=(
            _directory_requirement("library_caches", "用户缓存目录", HOME / "Library" / "Caches", required=True, description="基础清理的用户缓存目录。"),
            _directory_requirement("library_logs", "用户日志目录", HOME / "Library" / "Logs", required=True, description="基础清理的用户日志目录。"),
            _directory_requirement("desktop", "桌面", HOME / "Desktop", required=False, description="候选文件和大型文件会扫描桌面。"),
            _directory_requirement("documents", "文稿", HOME / "Documents", required=False, description="候选文件和大型文件会扫描文稿目录。"),
            _directory_requirement("downloads", "下载", HOME / "Downloads", required=False, description="候选文件、安装文件和下载文件会扫描下载目录。"),
        ),
    ),
    "images": FeaturePermissionSpec(
        key="images",
        name="图片管理",
        requirements=(
            _directory_requirement("desktop", "桌面", HOME / "Desktop", required=True, description="截图清理依赖桌面目录。"),
            _directory_requirement("downloads", "下载", HOME / "Downloads", required=True, description="下载图片整理依赖下载目录。"),
            _directory_requirement("photos_library", "照片图库", HOME / "Pictures" / "Photos Library.photoslibrary", required=True, description="照片管理会读取 Photos Library.photoslibrary。"),
            _directory_requirement("pictures", "图片", HOME / "Pictures", required=False, description="图片目录中的独立图片文件。"),
        ),
    ),
    "space": FeaturePermissionSpec(
        key="space",
        name="磁盘空间",
        requirements=(
            _directory_requirement("desktop", "桌面", HOME / "Desktop", required=True, description="磁盘空间分析会统计桌面目录。"),
            _directory_requirement("downloads", "下载", HOME / "Downloads", required=True, description="磁盘空间分析会统计下载目录。"),
            _directory_requirement("documents", "文稿", HOME / "Documents", required=True, description="磁盘空间分析会统计文稿目录。"),
            _directory_requirement("library", "Library", HOME / "Library", required=False, description="磁盘空间分析可选统计 Library。"),
        ),
    ),
    "caches": FeaturePermissionSpec(
        key="caches",
        name="软件缓存",
        requirements=(
            _directory_requirement("library_caches", "Library/Caches", HOME / "Library" / "Caches", required=False, description="浏览器和部分应用缓存根目录。"),
            _directory_requirement("application_support", "Application Support", HOME / "Library" / "Application Support", required=False, description="Cursor、VS Code、Slack 等缓存根目录。"),
            _directory_requirement("containers", "Containers", HOME / "Library" / "Containers", required=False, description="Safari、网易云、微信等容器缓存根目录。"),
            _directory_requirement("group_containers", "Group Containers", HOME / "Library" / "Group Containers", required=False, description="微信、QQ、钉钉等共享容器缓存根目录。"),
        ),
    ),
    "applications": FeaturePermissionSpec(
        key="applications",
        name="应用程序",
        requirements=(
            _directory_requirement("applications", "Applications", Path("/Applications"), required=False, description="用于识别系统中已安装的 App。"),
            _directory_requirement("user_applications", "用户 Applications", HOME / "Applications", required=False, description="用于识别用户目录中的 App。"),
            _directory_requirement("library_caches", "Library/Caches", HOME / "Library" / "Caches", required=False, description="应用残留扫描目录。"),
            _directory_requirement("library_logs", "Library/Logs", HOME / "Library" / "Logs", required=False, description="应用残留扫描目录。"),
            _directory_requirement("preferences", "Preferences", HOME / "Library" / "Preferences", required=False, description="应用偏好设置扫描目录。"),
            _directory_requirement("application_support", "Application Support", HOME / "Library" / "Application Support", required=False, description="应用支持目录残留扫描。"),
            _directory_requirement("containers", "Containers", HOME / "Library" / "Containers", required=False, description="容器残留扫描目录。"),
            _directory_requirement("group_containers", "Group Containers", HOME / "Library" / "Group Containers", required=False, description="共享容器残留扫描目录。"),
        ),
    ),
    "startup": FeaturePermissionSpec(
        key="startup",
        name="开机启动",
        requirements=(
            _automation_requirement("system_events", "System Events 自动化控制", required=True, description="读取和关闭登录项需要自动化权限。"),
            _directory_requirement("launch_agents", "LaunchAgents", HOME / "Library" / "LaunchAgents", required=False, description="后台项目会读取用户级 LaunchAgents。"),
        ),
    ),
}


def feature_directory_map() -> list[dict]:
    rows: list[dict] = []
    for spec in FEATURE_SPECS.values():
        rows.append(
            {
                "key": spec.key,
                "name": spec.name,
                "requirements": [
                    {
                        "key": requirement.key,
                        "name": requirement.name,
                        "kind": requirement.kind,
                        "path": requirement.path,
                        "required": requirement.required,
                        "description": requirement.description,
                        "section": requirement.section,
                    }
                    for requirement in spec.requirements
                ],
            }
        )
    return rows


def _directory_status(requirement: PermissionRequirement) -> dict:
    path = Path(requirement.path)
    exists = path.exists()
    accessible = False
    error = ""
    if exists:
        try:
            with os.scandir(path) as iterator:
                next(iterator, None)
            accessible = True
        except PermissionError as exc:
            error = str(exc)
        except OSError as exc:
            error = str(exc)
    return {
        "key": requirement.key,
        "name": requirement.name,
        "kind": requirement.kind,
        "path": str(path),
        "required": requirement.required,
        "section": requirement.section,
        "description": requirement.description,
        "exists": exists,
        "accessible": accessible,
        "error": error,
        "issue": exists and not accessible,
    }


def _automation_status(requirement: PermissionRequirement) -> dict:
    script = (
        'var se = Application("System Events");'
        'se.includeStandardAdditions = true;'
        'se.name();'
        '"ok";'
    )
    accessible = False
    error = ""
    try:
        completed = subprocess.run(
            ["osascript", "-l", "JavaScript"],
            input=script,
            text=True,
            capture_output=True,
            check=True,
        )
        accessible = completed.stdout.strip() == "ok"
    except subprocess.CalledProcessError as exc:
        combined = "\n".join(part for part in [exc.stdout, exc.stderr] if part).strip()
        error = combined or str(exc)
    except OSError as exc:
        error = str(exc)
    return {
        "key": requirement.key,
        "name": requirement.name,
        "kind": requirement.kind,
        "path": "",
        "required": requirement.required,
        "section": requirement.section,
        "description": requirement.description,
        "exists": True,
        "accessible": accessible,
        "error": error,
        "issue": not accessible,
    }


def _check_requirement(requirement: PermissionRequirement) -> dict:
    if requirement.kind == "automation":
        return _automation_status(requirement)
    return _directory_status(requirement)


def evaluate_feature_permissions(feature_keys: list[str] | tuple[str, ...]) -> dict:
    features: list[dict] = []
    blocked = False
    repair_sections: list[str] = []
    for feature_key in feature_keys:
        spec = FEATURE_SPECS.get(feature_key)
        if not spec:
            continue
        checked = [_check_requirement(requirement) for requirement in spec.requirements]
        required_missing = [item for item in checked if item["required"] and item["issue"]]
        optional_missing = [item for item in checked if not item["required"] and item["issue"]]
        if required_missing:
            blocked = True
        for item in required_missing + optional_missing:
            if item["section"] not in repair_sections:
                repair_sections.append(item["section"])
        features.append(
            {
                "key": spec.key,
                "name": spec.name,
                "requirements": checked,
                "required_missing": required_missing,
                "optional_missing": optional_missing,
                "has_issue": bool(required_missing or optional_missing),
                "blocked": bool(required_missing),
            }
        )
    affected = [feature for feature in features if feature["has_issue"]]
    return {
        "features": features,
        "affected_features": affected,
        "blocked": blocked,
        "has_issues": bool(affected),
        "repair_sections": repair_sections,
    }


def build_preflight_message(result: dict, *, overview_mode: bool = False) -> tuple[str, str]:
    affected = result.get("affected_features") or []
    if not affected:
        return "", ""

    blocked = bool(result.get("blocked"))
    title = "无法开始扫描" if blocked and not overview_mode else "扫描权限提示"
    lines: list[str] = []

    if blocked and not overview_mode:
        lines.append("当前缺少本功能的必选权限，暂时不能开始扫描。")
    else:
        lines.append("当前有部分目录或权限未开启。")
        if overview_mode:
            lines.append("全面检查会跳过缺少必选权限的模块，只扫描当前已授权的部分。")
        else:
            lines.append("你可以继续扫描已授权目录，也可以先去系统设置补齐权限。")

    for feature in affected:
        lines.extend(["", f"{feature['name']}："])
        if feature["required_missing"]:
            lines.append("必选目录 / 权限：")
            for item in feature["required_missing"]:
                suffix = f"（{item['path']}）" if item["path"] else ""
                lines.append(f"- {item['name']}{suffix}")
        if feature["optional_missing"]:
            lines.append("可选目录 / 权限：")
            for item in feature["optional_missing"]:
                suffix = f"（{item['path']}）" if item["path"] else ""
                lines.append(f"- {item['name']}{suffix}")

    lines.extend(
        [
            "",
            "处理建议：",
            "- 先点击“打开系统设置”开启对应权限。",
            "- 权限修改后请完全退出应用，再重新打开后扫描。",
        ]
    )
    return title, "\n".join(lines)
