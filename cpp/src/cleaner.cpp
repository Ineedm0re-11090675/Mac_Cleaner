#include "cleaner.hpp"

#include <algorithm>
#include <cctype>
#include <chrono>
#include <cstdlib>
#include <deque>
#include <filesystem>
#include <fstream>
#include <unordered_map>
#include <unordered_set>
#include <system_error>

namespace cleaner {
namespace fs = std::filesystem;

namespace {

constexpr std::size_t kSampleLimit = 5;
constexpr std::size_t kDetailedPathLimit = 20;
constexpr std::size_t kTopLargeFileLimit = 10;
constexpr std::size_t kTopAppCacheFileLimit = 20;
constexpr std::uintmax_t kDuplicateMinSize = 1ULL * 1024ULL * 1024ULL;
constexpr std::uintmax_t kOldLargeFileMinSize = 200ULL * 1024ULL * 1024ULL;
constexpr std::uintmax_t kDownloadCandidateMinSize = 20ULL * 1024ULL * 1024ULL;
constexpr long long kOldLargeFileMinDays = 120;
constexpr long long kDownloadCandidateMinDays = 30;

bool starts_with(const std::string& value, const std::string& prefix) {
    return value.rfind(prefix, 0) == 0;
}

std::string to_lower_copy(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) {
        return static_cast<char>(std::tolower(ch));
    });
    return value;
}

bool contains(const std::string& value, const std::string& needle) {
    return value.find(needle) != std::string::npos;
}

std::string classify_by_extension(const fs::path& path);

bool looks_like_installer_archive_name(const std::string& raw_name_lower) {
    return contains(raw_name_lower, "install") ||
           contains(raw_name_lower, "installer") ||
           contains(raw_name_lower, "setup") ||
           contains(raw_name_lower, "pkg");
}

bool is_installer_file(const fs::path& path) {
    const std::string ext = to_lower_copy(path.extension().string());
    const std::string name = to_lower_copy(path.filename().string());
    if (ext == ".dmg" || ext == ".pkg" || ext == ".mpkg" || ext == ".xip" || ext == ".iso") {
        return true;
    }
    if ((ext == ".zip" || ext == ".rar" || ext == ".7z" || ext == ".tar" || ext == ".gz") &&
        looks_like_installer_archive_name(name)) {
        return true;
    }
    return false;
}

std::string installer_note_for(const fs::path& path) {
    const std::string ext = to_lower_copy(path.extension().string());
    if (ext == ".dmg") return "磁盘镜像安装包";
    if (ext == ".pkg" || ext == ".mpkg") return "macOS 安装包";
    if (ext == ".xip") return "签名安装压缩包";
    if (ext == ".iso") return "镜像安装文件";
    if (ext == ".zip" || ext == ".rar" || ext == ".7z" || ext == ".tar" || ext == ".gz") return "安装压缩包";
    return "安装文件";
}

bool is_download_candidate(const fs::path& path, std::uintmax_t file_size, long long age_days_value, const std::string& home) {
    const std::string raw = path.string();
    const std::string downloads_root = home + "/Downloads";
    if (!starts_with(raw, downloads_root)) {
        return false;
    }
    if (file_size >= kDownloadCandidateMinSize) {
        return true;
    }
    return age_days_value >= kDownloadCandidateMinDays;
}

std::string download_note_for(const fs::path& path, std::uintmax_t file_size, long long age_days_value) {
    const std::string readable_type = classify_by_extension(path);
    if (file_size >= kDownloadCandidateMinSize && age_days_value >= kDownloadCandidateMinDays) {
        return "下载目录中的大文件，且较久没有改动";
    }
    if (file_size >= kDownloadCandidateMinSize) {
        return "下载目录中的大文件，建议确认是否仍需要";
    }
    if (age_days_value >= kDownloadCandidateMinDays) {
        return "下载目录中的旧文件，建议确认是否仍需要";
    }
    if (!readable_type.empty()) {
        return readable_type;
    }
    return "下载目录中的普通文件";
}

bool should_skip_path(const fs::path& path, const std::string& home) {
    const std::string raw = path.string();
    const std::vector<std::string> protected_prefixes = {
        "/System",
        "/Library",
        "/Applications",
        "/usr",
        "/bin",
        "/sbin",
        "/opt/homebrew",
        home + "/Library/Application Support"
    };

    for (const auto& prefix : protected_prefixes) {
        if (starts_with(raw, prefix)) {
            return true;
        }
    }
    return false;
}

CategoryReport make_category(std::string key,
                             std::string name,
                             std::string description,
                             std::vector<std::string> roots,
                             bool cleanable = true) {
    CategoryReport category;
    category.key = std::move(key);
    category.name = std::move(name);
    category.description = std::move(description);
    category.roots = std::move(roots);
    category.cleanable = cleanable;
    return category;
}

void maybe_add_sample(CategoryReport& category, const FileEntry& entry) {
    category.samples.push_back(entry);
    std::sort(category.samples.begin(), category.samples.end(), [](const FileEntry& left, const FileEntry& right) {
        if (left.size != right.size) {
            return left.size > right.size;
        }
        return left.path < right.path;
    });
    if (category.samples.size() > kSampleLimit) {
        category.samples.resize(kSampleLimit);
    }
}

bool key_selected(const std::vector<std::string>& selected_keys, const std::string& key) {
    return selected_keys.empty() ||
           std::find(selected_keys.begin(), selected_keys.end(), key) != selected_keys.end();
}

void add_limited_path(std::vector<std::string>& paths, std::size_t& truncated_count, const std::string& path) {
    if (paths.size() < kDetailedPathLimit) {
        paths.push_back(path);
    } else {
        truncated_count += 1;
    }
}

void add_limited_file(std::vector<FileEntry>& files, std::size_t& truncated_count, const FileEntry& file) {
    if (files.size() < kDetailedPathLimit) {
        files.push_back(file);
    } else {
        truncated_count += 1;
    }
}

void add_top_ranked_file(std::vector<FileEntry>& files, const FileEntry& file, std::size_t limit) {
    files.push_back(file);
    std::sort(files.begin(), files.end(), [](const FileEntry& left, const FileEntry& right) {
        if (left.size != right.size) {
            return left.size > right.size;
        }
        return left.path < right.path;
    });
    if (files.size() > limit) {
        files.resize(limit);
    }
}

std::vector<std::string> build_candidate_roots(const std::string& home) {
    return {
        home + "/Desktop",
        home + "/Documents",
        home + "/Downloads"
    };
}

long long age_in_days(const fs::file_time_type& file_time) {
    const auto now_file = fs::file_time_type::clock::now();
    const auto delta = now_file - file_time;
    const auto hours = std::chrono::duration_cast<std::chrono::hours>(delta).count();
    return hours / 24;
}

std::string hash_file_contents(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        return {};
    }

    std::uint64_t hash = 1469598103934665603ULL;
    char buffer[8192];
    while (input.read(buffer, sizeof(buffer)) || input.gcount() > 0) {
        const auto bytes = static_cast<std::size_t>(input.gcount());
        for (std::size_t i = 0; i < bytes; ++i) {
            hash ^= static_cast<unsigned char>(buffer[i]);
            hash *= 1099511628211ULL;
        }
    }

    return std::to_string(hash);
}

std::string classify_by_extension(const fs::path& path) {
    const std::string ext = to_lower_copy(path.extension().string());
    if (ext == ".jpg" || ext == ".jpeg" || ext == ".png" || ext == ".gif" || ext == ".webp" || ext == ".heic") {
        return "图片文件";
    }
    if (ext == ".mp4" || ext == ".mov" || ext == ".webm" || ext == ".mkv") {
        return "视频文件";
    }
    if (ext == ".mp3" || ext == ".aac" || ext == ".m4a" || ext == ".flac" || ext == ".ogg" || ext == ".wav") {
        return "音频文件";
    }
    if (ext == ".json" || ext == ".plist" || ext == ".log" || ext == ".txt") {
        return "文本/日志文件";
    }
    if (ext == ".uc!") {
        return "音频缓存片段";
    }
    if (ext == ".bundle" || ext == ".pak" || ext == ".dat" || ext == ".dll" || ext == ".dylib") {
        return "程序资源缓存";
    }
    return {};
}

std::string describe_browser_cache_path(const std::string& raw, const std::string& browser_name) {
    if (contains(raw, "/code cache/")) {
        return browser_name + "脚本代码缓存";
    }
    if (contains(raw, "/cache_data/") || contains(raw, "/networkcache/") || contains(raw, "/cache/")) {
        return browser_name + "网页资源缓存";
    }
    if (contains(raw, "/cachestorage/") || contains(raw, "/storage/")) {
        return browser_name + "网站离线缓存";
    }
    if (contains(raw, "/gpucache/") || contains(raw, "/dawncache/")) {
        return browser_name + "图形渲染缓存";
    }
    if (contains(raw, "/fscacheddata/")) {
        return browser_name + "文件系统缓存";
    }
    return browser_name + "缓存文件";
}

std::string describe_app_cache_file(const std::string& key, const fs::path& path) {
    const std::string raw = to_lower_copy(path.string());

    if (key == "chrome_cache") {
        return describe_browser_cache_path(raw, "Chrome ");
    }
    if (key == "edge_cache") {
        return describe_browser_cache_path(raw, "Edge ");
    }
    if (key == "firefox_cache") {
        return describe_browser_cache_path(raw, "Firefox ");
    }
    if (key == "safari_cache") {
        return describe_browser_cache_path(raw, "Safari ");
    }
    if (key == "cursor_cache") {
        return describe_browser_cache_path(raw, "Cursor ");
    }
    if (key == "vscode_cache") {
        return describe_browser_cache_path(raw, "VS Code ");
    }
    if (key == "slack_cache") {
        return describe_browser_cache_path(raw, "Slack ");
    }
    if (key == "discord_cache") {
        return describe_browser_cache_path(raw, "Discord ");
    }
    if (key == "netease_music_cache") {
        if (contains(raw, "/online_play_cache/")) return "在线音乐缓存";
        if (contains(raw, "/otimagewebcache/") || contains(raw, "/sdimagecache/")) return "封面图片缓存";
        if (contains(raw, "/mediacache/")) return "媒体缓存";
        if (contains(raw, "/cache_data/") || contains(raw, "/cefcache/") || contains(raw, "/code cache/")) return "网页内核缓存";
        if (contains(raw, "/download/")) return "下载缓存";
        if (contains(raw, "/library/caches/")) return "网易云程序缓存";
        return "网易云缓存文件";
    }
    if (key == "wechat_cache") {
        if (contains(raw, "/library/caches/")) return "微信程序缓存";
        if (contains(raw, "/app_data/radium/cache/")) return "微信网页缓存";
        if (contains(raw, "/app_data/radium/web/profiles/") && contains(raw, "/code cache/")) return "微信网页脚本缓存";
        if (contains(raw, "/app_data/radium/web/profiles/") && (contains(raw, "/gpucache/") || contains(raw, "/dawngraphitecache/"))) return "微信网页图形缓存";
        if (contains(raw, "/app_data/radium/web/profiles/") && contains(raw, "/indexeddb/")) return "微信网页离线数据缓存";
        if (contains(raw, "/app_data/radium/web/profiles/") && contains(raw, "/session storage/")) return "微信网页会话缓存";
        if (contains(raw, "/app_data/radium/web/")) return "微信网页内核缓存";
        if (contains(raw, "/app_data/radium/xeditor/cache/")) return "微信编辑器缓存";
        if (contains(raw, "/app_data/radium/xfile/cache/")) return "微信文件缓存";
        if (contains(raw, "/app_data/net/cdncomm/cdn/download/")) return "微信 CDN 下载缓存";
        if (contains(raw, "/app_data/radium/applet/icon/")) return "微信小程序图标缓存";
        if (contains(raw, "/app_data/radium/wmpfcache/")) return "微信小程序缓存";
        if (contains(raw, "/xwechat_files/") && contains(raw, "/temp/head_image/")) return "微信头像临时缓存";
        if (contains(raw, "/xwechat_files/") && contains(raw, "/all_users/head_imgs/")) return "微信头像缓存";
        if (contains(raw, "/xwechat_files/") && contains(raw, "/cache/")) return "微信媒体缓存";
        if (contains(raw, "/xwechat_files/") && contains(raw, "/temp/")) return "微信临时文件缓存";
        if (contains(raw, "/business/emoticon/temp/")) return "微信表情临时缓存";
        if (contains(raw, "/business/emoticon/thumb/") || contains(raw, "/business/emoticon/thumbstore/")) return "微信表情缩略图缓存";
        if (contains(raw, "/business/favorite/thumb/")) return "微信收藏缩略图";
        if (contains(raw, "/business/favorite/mid/")) return "微信收藏中间图缓存";
        if (contains(raw, "/msg/video/")) return "微信视频缓存";
        if (contains(raw, "/msg/file/")) return "微信文件缓存";
        if (contains(raw, "/msg/attach/")) return "微信聊天附件缓存";
        return {};
    }
    if (key == "qq_cache") {
        if (contains(raw, "/library/caches/")) return "QQ 程序缓存";
        if (contains(raw, "/video/") && contains(raw, "/thumbtemp/")) return "QQ 视频临时缩略图";
        if (contains(raw, "/video/") && contains(raw, "/thumb/")) return "QQ 视频缩略图缓存";
        if (contains(raw, "/file/") && contains(raw, "/thumbtemp/")) return "QQ 文件临时缩略图";
        if (contains(raw, "/file/") && contains(raw, "/thumb/")) return "QQ 文件缩略图缓存";
        if (contains(raw, "/flashfransfer/thumb")) return "QQ 闪传缩略图缓存";
        if (contains(raw, "/upload_temp")) return "QQ 上传临时文件";
        if (contains(raw, "/emoji/emoji-recv/") && contains(raw, "/oritemp/")) return "QQ 表情原图临时缓存";
        if (contains(raw, "/emoji/emoji-recv/") && (contains(raw, "/thumb/") || contains(raw, "/thumbtemp/"))) return "QQ 表情缩略图缓存";
        if (contains(raw, "/emoji/emoji-resource/") || contains(raw, "/baseemojisyastems/")) return "QQ 表情资源缓存";
        if (contains(raw, "/log-cache") || contains(raw, "/global/nt_temp")) return "QQ 临时缓存";
        if (contains(raw, "/dynamic_package/")) return "QQ 动态资源缓存";
        return {};
    }
    if (key == "dingtalk_cache") {
        if (contains(raw, "/library/caches/")) return "钉钉程序缓存";
        if (contains(raw, "/resource_cache/")) return "钉钉直播资源缓存";
        if (contains(raw, "/downloaddefaultemotion/")) return "钉钉表情资源缓存";
        if (contains(raw, "/portrait/")) return "钉钉头像缓存";
        return {};
    }
    if (key == "spotify_cache") {
        if (contains(raw, "/persistentcache/")) return "Spotify 音频与资源缓存";
        if (contains(raw, "/browser/") || contains(raw, "/storage/")) return "Spotify 网页内核缓存";
        return "Spotify 缓存文件";
    }
    if (key == "steam_cache") {
        if (contains(raw, "/htmlcache/")) return "Steam 商店网页缓存";
        if (contains(raw, "/appcache/") || contains(raw, "/httpcache/")) return "Steam 程序缓存";
        return "Steam 缓存文件";
    }
    if (key == "zoom_cache") {
        if (contains(raw, "/webviewcache/") || contains(raw, "/cefcache/")) return "Zoom 网页内核缓存";
        if (contains(raw, "/cache/")) return "Zoom 缓存文件";
        return "Zoom 缓存文件";
    }

    const std::string classified = classify_by_extension(path);
    if (!classified.empty()) {
        return classified;
    }
    if (contains(raw, "/library/caches/")) {
        return "程序缓存文件";
    }
    if (contains(raw, "/application support/")) {
        return "应用资源缓存";
    }
    return "缓存文件";
}

std::vector<std::string> build_app_cache_scan_roots(const std::string& key, const std::string& home) {
    if (key == "wechat_cache") {
        return {
            home + "/Library/Containers/com.tencent.xinWeChat/Data/Library/Caches",
            home + "/Library/Containers/com.tencent.xinWeChat/Data/Documents/app_data",
            home + "/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files"
        };
    }
    if (key == "qq_cache") {
        return {
            home + "/Library/Containers/com.tencent.qq/Data/Library/Application Support/QQ"
        };
    }
    if (key == "dingtalk_cache") {
        return {
            home + "/Library/Group Containers/5ZSL2CJU2T.group.com.dingtalk.mac.tblive/Library/Application Support/dinglive/dingtalk_resources",
            home + "/Library/Group Containers/5ZSL2CJU2T.group.com.dingtalk.mac.tblive/Library/Application Support/dinglive/portrait"
        };
    }
    return {};
}

template <typename OnFile>
void walk_regular_files(const fs::path& root, OnFile on_file) {
    std::error_code ec;
    if (!fs::exists(root, ec) || ec) {
        return;
    }

    std::deque<fs::path> pending;
    pending.push_back(root);

    while (!pending.empty()) {
        const fs::path current = pending.front();
        pending.pop_front();

        fs::directory_iterator it(current, fs::directory_options::skip_permission_denied, ec);
        fs::directory_iterator end;
        if (ec) {
            ec.clear();
            continue;
        }

        while (it != end) {
            fs::directory_entry entry;
            try {
                entry = *it;
            } catch (const fs::filesystem_error&) {
                std::error_code increment_ec;
                it.increment(increment_ec);
                continue;
            }

            std::error_code status_ec;
            if (entry.is_directory(status_ec)) {
                pending.push_back(entry.path());
            } else if (entry.is_regular_file(status_ec)) {
                on_file(entry);
            }

            std::error_code increment_ec;
            it.increment(increment_ec);
            if (increment_ec) {
                increment_ec.clear();
            }
        }
    }
}

void scan_category_files(CategoryReport& category) {
    for (const auto& root : category.roots) {
        std::error_code ec;
        if (!fs::exists(root, ec) || ec) {
            continue;
        }

        walk_regular_files(root, [&](const fs::directory_entry& entry) {
            std::error_code size_ec;
            const auto file_size = entry.file_size(size_ec);
            if (size_ec) {
                return;
            }

            std::error_code time_ec;
            const auto last_write = entry.last_write_time(time_ec);
            const long long age_days_value = time_ec ? -1 : age_in_days(last_write);

            FileEntry sample;
            sample.path = entry.path().string();
            sample.group = category.name;
            sample.size = file_size;
            sample.age_days = age_days_value;
            category.file_count += 1;
            category.total_bytes += file_size;
            maybe_add_sample(category, sample);
        });
    }
}

std::vector<CleanStats> clean_category_collection(const std::vector<CategoryReport>& categories,
                                                 const std::vector<std::string>& selected_keys,
                                                 bool dry_run) {
    const std::string home = get_home_directory();
    std::vector<CleanStats> results;

    for (const auto& category : categories) {
        if (!key_selected(selected_keys, category.key) || !category.cleanable) {
            continue;
        }

        CleanStats stats;
        stats.key = category.key;
        stats.dry_run = dry_run;

        for (const auto& root : category.roots) {
            std::error_code ec;
            if (!fs::exists(root, ec) || ec) {
                continue;
            }

            walk_regular_files(root, [&](const fs::directory_entry& entry) {
                const fs::path path = entry.path();
                std::error_code size_ec;
                const auto file_size = entry.file_size(size_ec);
                if (size_ec) {
                    add_limited_path(stats.skipped_paths, stats.skipped_paths_truncated, path.string());
                    return;
                }

                if (should_skip_path(path, home)) {
                    add_limited_path(stats.skipped_paths, stats.skipped_paths_truncated, path.string());
                    return;
                }

                if (dry_run) {
                    stats.deleted_files += 1;
                    stats.reclaimed_bytes += file_size;
                    add_limited_path(stats.deleted_paths, stats.deleted_paths_truncated, path.string());
                    return;
                }

                std::error_code remove_ec;
                if (fs::remove(path, remove_ec)) {
                    stats.deleted_files += 1;
                    stats.reclaimed_bytes += file_size;
                    add_limited_path(stats.deleted_paths, stats.deleted_paths_truncated, path.string());
                } else {
                    add_limited_path(stats.skipped_paths, stats.skipped_paths_truncated, path.string());
                }
            });
        }

        results.push_back(std::move(stats));
    }

    return results;
}

}  // namespace

std::string get_home_directory() {
    if (const char* home = std::getenv("HOME")) {
        return std::string(home);
    }
    return {};
}

std::vector<CategoryReport> build_default_categories() {
    const std::string home = get_home_directory();
    return {
        make_category("user_cache", "User Cache", "App cache files in the user Library.", {home + "/Library/Caches"}),
        make_category("user_logs", "User Logs", "Log files in the user Library.", {home + "/Library/Logs"}),
        make_category("trash", "Trash", "Files currently in the Trash.", {home + "/.Trash"}),
        make_category("downloads_large_files", "Downloads Large Files", "Large files found in Downloads.", {home + "/Downloads"}, false)
    };
}

std::vector<CategoryReport> build_app_cache_categories() {
    const std::string home = get_home_directory();
    return {
        make_category("chrome_cache", "Google Chrome 缓存", "Google Chrome 的网页资源缓存和代码缓存。", {
            home + "/Library/Caches/Google/Chrome"
        }),
        make_category("edge_cache", "Microsoft Edge 缓存", "Microsoft Edge 的网页资源缓存和代码缓存。", {
            home + "/Library/Caches/Microsoft Edge"
        }),
        make_category("firefox_cache", "Firefox 缓存", "Firefox 的浏览器缓存目录。", {
            home + "/Library/Caches/Firefox"
        }),
        make_category("safari_cache", "Safari 缓存", "Safari 的缓存目录。", {
            home + "/Library/Caches/com.apple.Safari",
            home + "/Library/Containers/com.apple.Safari/Data/Library/Caches"
        }),
        make_category("cursor_cache", "Cursor 缓存", "Cursor 的编辑器缓存和网页内核缓存。", {
            home + "/Library/Application Support/Cursor/Cache",
            home + "/Library/Application Support/Cursor/Code Cache",
            home + "/Library/Application Support/Cursor/GPUCache",
            home + "/Library/Application Support/Cursor/CachedData",
            home + "/Library/Application Support/Cursor/DawnCache",
            home + "/Library/Application Support/Cursor/Service Worker/CacheStorage"
        }),
        make_category("vscode_cache", "VS Code 缓存", "Visual Studio Code 的编辑器缓存和网页内核缓存。", {
            home + "/Library/Application Support/Code/Cache",
            home + "/Library/Application Support/Code/Code Cache",
            home + "/Library/Application Support/Code/GPUCache",
            home + "/Library/Application Support/Code/CachedData",
            home + "/Library/Application Support/Code/DawnCache",
            home + "/Library/Application Support/Code/Service Worker/CacheStorage"
        }),
        make_category("slack_cache", "Slack 缓存", "Slack 的网页资源缓存和离线缓存。", {
            home + "/Library/Application Support/Slack/Cache",
            home + "/Library/Application Support/Slack/Code Cache",
            home + "/Library/Application Support/Slack/GPUCache",
            home + "/Library/Application Support/Slack/CachedData",
            home + "/Library/Application Support/Slack/Service Worker/CacheStorage",
            home + "/Library/Application Support/Slack/blob_storage"
        }),
        make_category("discord_cache", "Discord 缓存", "Discord 的网页资源缓存和离线缓存。", {
            home + "/Library/Application Support/discord/Cache",
            home + "/Library/Application Support/discord/Code Cache",
            home + "/Library/Application Support/discord/GPUCache",
            home + "/Library/Application Support/discord/CachedData",
            home + "/Library/Application Support/discord/Service Worker/CacheStorage",
            home + "/Library/Application Support/discord/blob_storage"
        }),
        make_category("netease_music_cache", "网易云音乐缓存", "网易云音乐的图片、网页和在线播放缓存。", {
            home + "/Library/Containers/com.netease.163music/Data/Library/Caches",
            home + "/Library/Containers/com.netease.163music/Data/Documents/storage/CEFCache",
            home + "/Library/Containers/com.netease.163music/Data/tmp/WebKit/MediaCache"
        }),
        make_category("spotify_cache", "Spotify 缓存", "Spotify 的音频缓存和网页资源缓存。", {
            home + "/Library/Application Support/Spotify/PersistentCache",
            home + "/Library/Application Support/Spotify/Browser/Cache"
        }),
        make_category("wechat_cache", "微信缓存", "微信的缓存目录，不包含聊天正文数据库。", {
            home + "/Library/Group Containers/5A4RE8SF68.com.tencent.xinWeChat/Library/Caches",
            home + "/Library/Containers/com.tencent.xinWeChat/Data/Library/Caches"
        }),
        make_category("qq_cache", "QQ 缓存", "QQ 的缓存目录，不包含聊天正文数据库。", {
            home + "/Library/Group Containers/FN2V63AD2J.com.tencent/Library/Caches",
            home + "/Library/Containers/com.tencent.qq/Data/Library/Caches"
        }),
        make_category("dingtalk_cache", "钉钉缓存", "钉钉的缓存目录，不包含聊天正文数据库。", {
            home + "/Library/Group Containers/5ZSL2CJU2T.com.dingtalk.mac/Library/Caches",
            home + "/Library/Containers/5ZSL2CJU2T.com.dingtalk.mac/Data/Library/Caches",
            home + "/Library/Containers/5ZSL2CJU2T.com.dingtalk.mac.tblive/Data/Library/Caches"
        }),
        make_category("steam_cache", "Steam 缓存", "Steam 的网页缓存和程序缓存。", {
            home + "/Library/Application Support/Steam/appcache",
            home + "/Library/Application Support/Steam/htmlcache",
            home + "/Library/Application Support/Steam/config/htmlcache"
        }),
        make_category("zoom_cache", "Zoom 缓存", "Zoom 的网页内核缓存。", {
            home + "/Library/Application Support/zoom.us/data/WebviewCache",
            home + "/Library/Application Support/zoom.us/data/cefcache"
        })
    };
}

ScanReport scan_categories(const std::vector<std::string>& selected_keys) {
    ScanReport report;
    auto categories = build_default_categories();
    const std::string home = get_home_directory();

    std::unordered_map<std::uintmax_t, std::vector<FileEntry>> duplicate_size_buckets;
    std::vector<FileEntry> old_large_files;
    std::vector<FileEntry> top_large_files;
    std::vector<FileEntry> installer_files;
    std::vector<FileEntry> download_files;
    const auto candidate_roots = build_candidate_roots(home);

    for (auto& category : categories) {
        if (!key_selected(selected_keys, category.key)) {
            continue;
        }

        for (const auto& root : category.roots) {
            std::error_code ec;
            if (!fs::exists(root, ec)) {
                continue;
            }

            if (category.key == "downloads_large_files") {
                for (const auto& entry : fs::directory_iterator(root, fs::directory_options::skip_permission_denied, ec)) {
                    if (ec || !entry.is_regular_file(ec)) {
                        continue;
                    }

                    const auto file_size = entry.file_size(ec);
                    if (ec || file_size < 100ULL * 1024ULL * 1024ULL) {
                        continue;
                    }

                    FileEntry sample;
                    sample.path = entry.path().string();
                    sample.size = file_size;
                    category.file_count += 1;
                    category.total_bytes += file_size;
                    maybe_add_sample(category, sample);
                }
                continue;
            }

            walk_regular_files(root, [&](const fs::directory_entry& entry) {
                std::error_code size_ec;
                const auto file_size = entry.file_size(size_ec);
                if (size_ec) {
                    return;
                }

                FileEntry sample;
                sample.path = entry.path().string();
                sample.size = file_size;
                category.file_count += 1;
                category.total_bytes += file_size;
                maybe_add_sample(category, sample);
            });
        }

        report.grand_total_bytes += category.total_bytes;
        report.categories.push_back(category);
    }

    for (const auto& root : candidate_roots) {
        walk_regular_files(root, [&](const fs::directory_entry& entry) {
            std::error_code size_ec;
            const auto file_size = entry.file_size(size_ec);
            if (size_ec || file_size == 0) {
                return;
            }

            std::error_code time_ec;
            const auto last_write = entry.last_write_time(time_ec);
            const long long age_days_value = time_ec ? -1 : age_in_days(last_write);
            const bool installer_file = is_installer_file(entry.path());

            if (file_size >= kDuplicateMinSize) {
                FileEntry duplicate_file;
                duplicate_file.path = entry.path().string();
                duplicate_file.size = file_size;
                duplicate_file.age_days = age_days_value;
                duplicate_size_buckets[file_size].push_back(std::move(duplicate_file));
            }

            if (file_size >= kOldLargeFileMinSize && age_days_value >= kOldLargeFileMinDays) {
                FileEntry stale_file;
                stale_file.path = entry.path().string();
                stale_file.size = file_size;
                stale_file.age_days = age_days_value;
                stale_file.note = "Large file not modified recently";
                old_large_files.push_back(std::move(stale_file));
            }

            if (installer_file) {
                FileEntry installer_entry;
                installer_entry.path = entry.path().string();
                installer_entry.size = file_size;
                installer_entry.age_days = age_days_value;
                installer_entry.note = installer_note_for(entry.path());
                installer_files.push_back(std::move(installer_entry));
            } else if (is_download_candidate(entry.path(), file_size, age_days_value, home)) {
                FileEntry download_entry;
                download_entry.path = entry.path().string();
                download_entry.size = file_size;
                download_entry.age_days = age_days_value;
                download_entry.note = download_note_for(entry.path(), file_size, age_days_value);
                download_files.push_back(std::move(download_entry));
            }

            FileEntry top_file;
            top_file.path = entry.path().string();
            top_file.size = file_size;
            top_file.age_days = age_days_value;
            top_file.note = "Large file ranked by size";
            add_top_ranked_file(top_large_files, top_file, kTopLargeFileLimit);
        });
    }

    report.large_files.key = "largest_files_top10";
    report.large_files.name = "Top 10 Largest Files";
    report.large_files.description = "Largest files in Desktop, Documents, and Downloads.";
    report.large_files.file_count = top_large_files.size();
    report.large_files.files = top_large_files;
    for (const auto& file : report.large_files.files) {
        report.large_files.total_bytes += file.size;
    }

    FindingReport stale_finding;
    stale_finding.key = "stale_large_files";
    stale_finding.name = "Long Unused Large Files";
    stale_finding.description = "Large files in Desktop, Documents, and Downloads not modified for at least 120 days.";
    std::sort(old_large_files.begin(), old_large_files.end(), [](const FileEntry& left, const FileEntry& right) {
        if (left.size != right.size) {
            return left.size > right.size;
        }
        return left.path < right.path;
    });
    for (const auto& file : old_large_files) {
        stale_finding.file_count += 1;
        stale_finding.total_bytes += file.size;
        add_limited_file(stale_finding.files, stale_finding.truncated_count, file);
    }
    if (stale_finding.file_count > 0) {
        report.grand_total_candidate_bytes += stale_finding.total_bytes;
        report.findings.push_back(std::move(stale_finding));
    }

    FindingReport installer_finding;
    installer_finding.key = "installer_files";
    installer_finding.name = "安装文件";
    installer_finding.description = "Desktop、Documents、Downloads 中的 DMG、PKG 和安装压缩包。";
    std::sort(installer_files.begin(), installer_files.end(), [](const FileEntry& left, const FileEntry& right) {
        if (left.size != right.size) {
            return left.size > right.size;
        }
        return left.path < right.path;
    });
    for (const auto& file : installer_files) {
        installer_finding.file_count += 1;
        installer_finding.total_bytes += file.size;
        add_limited_file(installer_finding.files, installer_finding.truncated_count, file);
    }
    if (installer_finding.file_count > 0) {
        report.grand_total_candidate_bytes += installer_finding.total_bytes;
        report.findings.push_back(std::move(installer_finding));
    }

    FindingReport download_finding;
    download_finding.key = "download_files";
    download_finding.name = "下载文件";
    download_finding.description = "Downloads 中较大的文件或较久未修改的文件。";
    std::sort(download_files.begin(), download_files.end(), [](const FileEntry& left, const FileEntry& right) {
        if (left.size != right.size) {
            return left.size > right.size;
        }
        return left.path < right.path;
    });
    for (const auto& file : download_files) {
        download_finding.file_count += 1;
        download_finding.total_bytes += file.size;
        add_limited_file(download_finding.files, download_finding.truncated_count, file);
    }
    if (download_finding.file_count > 0) {
        report.grand_total_candidate_bytes += download_finding.total_bytes;
        report.findings.push_back(std::move(download_finding));
    }

    FindingReport duplicate_finding;
    duplicate_finding.key = "duplicate_files";
    duplicate_finding.name = "Duplicate Files";
    duplicate_finding.description = "Files with identical size and content hash in Desktop, Documents, and Downloads.";
    for (auto& [size, files] : duplicate_size_buckets) {
        if (files.size() < 2) {
            continue;
        }

        std::unordered_map<std::string, std::vector<FileEntry>> by_hash;
        for (const auto& file : files) {
            const std::string hash = hash_file_contents(file.path);
            if (!hash.empty()) {
                by_hash[hash].push_back(file);
            }
        }

        for (auto& [hash, group] : by_hash) {
            if (group.size() < 2) {
                continue;
            }

            std::sort(group.begin(), group.end(), [](const FileEntry& left, const FileEntry& right) {
                return left.path < right.path;
            });

            const std::size_t reclaimable_copies = group.size() - 1;
            duplicate_finding.file_count += group.size();
            duplicate_finding.total_bytes += size * reclaimable_copies;

            for (std::size_t i = 0; i < group.size(); ++i) {
                auto file = group[i];
                file.note = (i == 0) ? "Keep one copy" : "Duplicate candidate";
                add_limited_file(duplicate_finding.files, duplicate_finding.truncated_count, file);
            }
        }
    }
    std::sort(duplicate_finding.files.begin(), duplicate_finding.files.end(), [](const FileEntry& left, const FileEntry& right) {
        if (left.size != right.size) {
            return left.size > right.size;
        }
        return left.path < right.path;
    });
    if (duplicate_finding.file_count > 0) {
        report.grand_total_candidate_bytes += duplicate_finding.total_bytes;
        report.findings.push_back(std::move(duplicate_finding));
    }

    return report;
}

AppCacheScanReport scan_app_cache_categories(const std::vector<std::string>& selected_keys) {
    AppCacheScanReport report;
    auto categories = build_app_cache_categories();
    std::vector<FileEntry> top_files;

    for (auto& category : categories) {
        if (!key_selected(selected_keys, category.key)) {
            continue;
        }

        std::unordered_set<std::string> seen_paths;
        const auto scan_roots = build_app_cache_scan_roots(category.key, get_home_directory());

        auto consume_root = [&](const std::string& root) {
            std::error_code ec;
            if (!fs::exists(root, ec) || ec) {
                return;
            }

            walk_regular_files(root, [&](const fs::directory_entry& entry) {
                const std::string path_string = entry.path().string();
                if (!seen_paths.insert(path_string).second) {
                    return;
                }

                const std::string description = describe_app_cache_file(category.key, entry.path());
                if (description.empty()) {
                    return;
                }

                std::error_code size_ec;
                const auto file_size = entry.file_size(size_ec);
                if (size_ec) {
                    return;
                }

                std::error_code time_ec;
                const auto last_write = entry.last_write_time(time_ec);
                const long long age_days_value = time_ec ? -1 : age_in_days(last_write);

                FileEntry file;
                file.path = path_string;
                file.group = category.name;
                file.size = file_size;
                file.age_days = age_days_value;
                file.note = description;

                category.file_count += 1;
                category.total_bytes += file_size;
                maybe_add_sample(category, file);
                add_top_ranked_file(top_files, file, kTopAppCacheFileLimit);
            });
        };

        for (const auto& root : category.roots) {
            consume_root(root);
        }
        for (const auto& root : scan_roots) {
            consume_root(root);
        }

        report.total_bytes += category.total_bytes;
        report.total_file_count += category.file_count;
        report.categories.push_back(category);
    }

    report.files = std::move(top_files);
    return report;
}

std::vector<CleanStats> clean_categories(const std::vector<std::string>& selected_keys, bool dry_run) {
    return clean_category_collection(build_default_categories(), selected_keys, dry_run);
}

std::vector<CleanStats> clean_app_cache_categories(const std::vector<std::string>& selected_keys, bool dry_run) {
    return clean_category_collection(build_app_cache_categories(), selected_keys, dry_run);
}

CleanStats clean_files(const std::vector<std::string>& file_paths, bool dry_run) {
    const std::string home = get_home_directory();
    CleanStats stats;
    stats.key = "selected_files";
    stats.dry_run = dry_run;

    for (const auto& raw_path : file_paths) {
        const fs::path path(raw_path);
        std::error_code ec;
        if (!fs::exists(path, ec) || ec || !fs::is_regular_file(path, ec) || ec) {
            add_limited_path(stats.skipped_paths, stats.skipped_paths_truncated, raw_path);
            continue;
        }

        if (should_skip_path(path, home)) {
            add_limited_path(stats.skipped_paths, stats.skipped_paths_truncated, raw_path);
            continue;
        }

        const auto file_size = fs::file_size(path, ec);
        if (ec) {
            add_limited_path(stats.skipped_paths, stats.skipped_paths_truncated, raw_path);
            continue;
        }

        if (dry_run) {
            stats.deleted_files += 1;
            stats.reclaimed_bytes += file_size;
            add_limited_path(stats.deleted_paths, stats.deleted_paths_truncated, raw_path);
            continue;
        }

        std::error_code remove_ec;
        if (fs::remove(path, remove_ec)) {
            stats.deleted_files += 1;
            stats.reclaimed_bytes += file_size;
            add_limited_path(stats.deleted_paths, stats.deleted_paths_truncated, raw_path);
        } else {
            add_limited_path(stats.skipped_paths, stats.skipped_paths_truncated, raw_path);
        }
    }

    return stats;
}

}  // namespace cleaner
