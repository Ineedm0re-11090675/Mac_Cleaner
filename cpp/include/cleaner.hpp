#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace cleaner {

struct FileEntry {
    std::string path;
    std::string group;
    std::uintmax_t size = 0;
    long long age_days = -1;
    std::string note;
};

struct CategoryReport {
    std::string key;
    std::string name;
    std::string description;
    std::vector<std::string> roots;
    std::vector<FileEntry> samples;
    std::uintmax_t total_bytes = 0;
    std::size_t file_count = 0;
    bool cleanable = true;
};

struct FindingReport {
    std::string key;
    std::string name;
    std::string description;
    std::vector<FileEntry> files;
    std::uintmax_t total_bytes = 0;
    std::size_t file_count = 0;
    std::size_t truncated_count = 0;
};

struct ScanReport {
    std::vector<CategoryReport> categories;
    FindingReport large_files;
    std::vector<FindingReport> findings;
    std::uintmax_t grand_total_bytes = 0;
    std::uintmax_t grand_total_candidate_bytes = 0;
};

struct AppCacheScanReport {
    std::vector<CategoryReport> categories;
    std::vector<FileEntry> files;
    std::uintmax_t total_bytes = 0;
    std::size_t total_file_count = 0;
    std::size_t truncated_count = 0;
};

struct CleanStats {
    std::string key;
    bool dry_run = true;
    std::size_t deleted_files = 0;
    std::uintmax_t reclaimed_bytes = 0;
    std::size_t deleted_paths_truncated = 0;
    std::size_t skipped_paths_truncated = 0;
    std::vector<std::string> deleted_paths;
    std::vector<std::string> skipped_paths;
};

std::string get_home_directory();
std::vector<CategoryReport> build_default_categories();
std::vector<CategoryReport> build_app_cache_categories();
ScanReport scan_categories(const std::vector<std::string>& selected_keys = {});
AppCacheScanReport scan_app_cache_categories(const std::vector<std::string>& selected_keys = {});
std::vector<CleanStats> clean_categories(const std::vector<std::string>& selected_keys, bool dry_run);
std::vector<CleanStats> clean_app_cache_categories(const std::vector<std::string>& selected_keys, bool dry_run);
CleanStats clean_files(const std::vector<std::string>& file_paths, bool dry_run);

}  // namespace cleaner
