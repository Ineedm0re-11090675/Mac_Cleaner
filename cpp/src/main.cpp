#include "cleaner.hpp"

#include <iomanip>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace {

std::string escape_json(const std::string& input) {
    std::ostringstream out;
    for (const char ch : input) {
        switch (ch) {
            case '\\':
                out << "\\\\";
                break;
            case '"':
                out << "\\\"";
                break;
            case '\n':
                out << "\\n";
                break;
            case '\r':
                out << "\\r";
                break;
            case '\t':
                out << "\\t";
                break;
            default:
                out << ch;
                break;
        }
    }
    return out.str();
}

void print_usage() {
    std::cerr << "Usage: mac_cleaner <scan|clean|clean-files|scan-app-caches|clean-app-caches> [args ...] [--dry-run] [--execute]\n";
}

void print_file_entry_json(const cleaner::FileEntry& file) {
    std::cout << "{";
    std::cout << "\"path\":\"" << escape_json(file.path) << "\",";
    std::cout << "\"group\":\"" << escape_json(file.group) << "\",";
    std::cout << "\"size\":" << file.size << ",";
    std::cout << "\"age_days\":" << file.age_days << ",";
    std::cout << "\"note\":\"" << escape_json(file.note) << "\"";
    std::cout << "}";
}

void print_scan_json(const cleaner::ScanReport& report) {
    std::cout << "{";
    std::cout << "\"grand_total_bytes\":" << report.grand_total_bytes << ",";
    std::cout << "\"grand_total_candidate_bytes\":" << report.grand_total_candidate_bytes << ",";
    std::cout << "\"categories\":[";

    for (std::size_t i = 0; i < report.categories.size(); ++i) {
        const auto& category = report.categories[i];
        if (i > 0) {
            std::cout << ",";
        }

        std::cout << "{";
        std::cout << "\"key\":\"" << escape_json(category.key) << "\",";
        std::cout << "\"name\":\"" << escape_json(category.name) << "\",";
        std::cout << "\"description\":\"" << escape_json(category.description) << "\",";
        std::cout << "\"cleanable\":" << (category.cleanable ? "true" : "false") << ",";
        std::cout << "\"total_bytes\":" << category.total_bytes << ",";
        std::cout << "\"file_count\":" << category.file_count << ",";
        std::cout << "\"roots\":[";
        for (std::size_t j = 0; j < category.roots.size(); ++j) {
            if (j > 0) {
                std::cout << ",";
            }
            std::cout << "\"" << escape_json(category.roots[j]) << "\"";
        }
        std::cout << "],";
        std::cout << "\"samples\":[";
        for (std::size_t j = 0; j < category.samples.size(); ++j) {
            if (j > 0) {
                std::cout << ",";
            }
            print_file_entry_json(category.samples[j]);
        }
        std::cout << "]";
        std::cout << "}";
    }
    std::cout << "],";
    std::cout << "\"large_files\":{";
    std::cout << "\"key\":\"" << escape_json(report.large_files.key) << "\",";
    std::cout << "\"name\":\"" << escape_json(report.large_files.name) << "\",";
    std::cout << "\"description\":\"" << escape_json(report.large_files.description) << "\",";
    std::cout << "\"total_bytes\":" << report.large_files.total_bytes << ",";
    std::cout << "\"file_count\":" << report.large_files.file_count << ",";
    std::cout << "\"truncated_count\":" << report.large_files.truncated_count << ",";
    std::cout << "\"files\":[";
    for (std::size_t j = 0; j < report.large_files.files.size(); ++j) {
        if (j > 0) {
            std::cout << ",";
        }
        print_file_entry_json(report.large_files.files[j]);
    }
    std::cout << "]";
    std::cout << "},";
    std::cout << "\"findings\":[";
    for (std::size_t i = 0; i < report.findings.size(); ++i) {
        const auto& finding = report.findings[i];
        if (i > 0) {
            std::cout << ",";
        }

        std::cout << "{";
        std::cout << "\"key\":\"" << escape_json(finding.key) << "\",";
        std::cout << "\"name\":\"" << escape_json(finding.name) << "\",";
        std::cout << "\"description\":\"" << escape_json(finding.description) << "\",";
        std::cout << "\"total_bytes\":" << finding.total_bytes << ",";
        std::cout << "\"file_count\":" << finding.file_count << ",";
        std::cout << "\"truncated_count\":" << finding.truncated_count << ",";
        std::cout << "\"files\":[";
        for (std::size_t j = 0; j < finding.files.size(); ++j) {
            if (j > 0) {
                std::cout << ",";
            }
            print_file_entry_json(finding.files[j]);
        }
        std::cout << "]";
        std::cout << "}";
    }
    std::cout << "]}";
}

void print_app_cache_scan_json(const cleaner::AppCacheScanReport& report) {
    std::cout << "{";
    std::cout << "\"total_bytes\":" << report.total_bytes << ",";
    std::cout << "\"total_file_count\":" << report.total_file_count << ",";
    std::cout << "\"truncated_count\":" << report.truncated_count << ",";
    std::cout << "\"categories\":[";
    for (std::size_t i = 0; i < report.categories.size(); ++i) {
        const auto& category = report.categories[i];
        if (i > 0) {
            std::cout << ",";
        }
        std::cout << "{";
        std::cout << "\"key\":\"" << escape_json(category.key) << "\",";
        std::cout << "\"name\":\"" << escape_json(category.name) << "\",";
        std::cout << "\"description\":\"" << escape_json(category.description) << "\",";
        std::cout << "\"cleanable\":" << (category.cleanable ? "true" : "false") << ",";
        std::cout << "\"total_bytes\":" << category.total_bytes << ",";
        std::cout << "\"file_count\":" << category.file_count << ",";
        std::cout << "\"roots\":[";
        for (std::size_t j = 0; j < category.roots.size(); ++j) {
            if (j > 0) {
                std::cout << ",";
            }
            std::cout << "\"" << escape_json(category.roots[j]) << "\"";
        }
        std::cout << "],";
        std::cout << "\"samples\":[";
        for (std::size_t j = 0; j < category.samples.size(); ++j) {
            if (j > 0) {
                std::cout << ",";
            }
            print_file_entry_json(category.samples[j]);
        }
        std::cout << "]";
        std::cout << "}";
    }
    std::cout << "],";
    std::cout << "\"files\":[";
    for (std::size_t i = 0; i < report.files.size(); ++i) {
        if (i > 0) {
            std::cout << ",";
        }
        print_file_entry_json(report.files[i]);
    }
    std::cout << "]";
    std::cout << "}";
}

void print_clean_json(const std::vector<cleaner::CleanStats>& stats_list) {
    std::cout << "{\"results\":[";
    for (std::size_t i = 0; i < stats_list.size(); ++i) {
        const auto& stats = stats_list[i];
        if (i > 0) {
            std::cout << ",";
        }

        std::cout << "{";
        std::cout << "\"key\":\"" << escape_json(stats.key) << "\",";
        std::cout << "\"dry_run\":" << (stats.dry_run ? "true" : "false") << ",";
        std::cout << "\"deleted_files\":" << stats.deleted_files << ",";
        std::cout << "\"reclaimed_bytes\":" << stats.reclaimed_bytes << ",";
        std::cout << "\"deleted_paths_truncated\":" << stats.deleted_paths_truncated << ",";
        std::cout << "\"skipped_paths_truncated\":" << stats.skipped_paths_truncated << ",";
        std::cout << "\"deleted_paths\":[";
        for (std::size_t j = 0; j < stats.deleted_paths.size(); ++j) {
            if (j > 0) {
                std::cout << ",";
            }
            std::cout << "\"" << escape_json(stats.deleted_paths[j]) << "\"";
        }
        std::cout << "],";
        std::cout << "\"skipped_paths\":[";
        for (std::size_t j = 0; j < stats.skipped_paths.size(); ++j) {
            if (j > 0) {
                std::cout << ",";
            }
            std::cout << "\"" << escape_json(stats.skipped_paths[j]) << "\"";
        }
        std::cout << "]";
        std::cout << "}";
    }
    std::cout << "]}";
}

}  // namespace

int main(int argc, char* argv[]) {
    if (argc < 2) {
        print_usage();
        return 1;
    }

    const std::string command = argv[1];
    bool dry_run = true;
    std::vector<std::string> arguments;

    for (int i = 2; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--dry-run") {
            dry_run = true;
        } else if (arg == "--execute") {
            dry_run = false;
        } else {
            arguments.push_back(arg);
        }
    }

    if (command == "scan") {
        print_scan_json(cleaner::scan_categories(arguments));
        return 0;
    }

    if (command == "scan-app-caches") {
        print_app_cache_scan_json(cleaner::scan_app_cache_categories(arguments));
        return 0;
    }

    if (command == "clean") {
        print_clean_json(cleaner::clean_categories(arguments, dry_run));
        return 0;
    }

    if (command == "clean-app-caches") {
        print_clean_json(cleaner::clean_app_cache_categories(arguments, dry_run));
        return 0;
    }

    if (command == "clean-files") {
        if (arguments.empty()) {
            print_usage();
            return 1;
        }

        std::ifstream input(arguments.front());
        if (!input) {
            std::cerr << "Failed to open manifest file: " << arguments.front() << "\n";
            return 1;
        }

        std::vector<std::string> file_paths;
        std::string line;
        while (std::getline(input, line)) {
            if (!line.empty()) {
                file_paths.push_back(line);
            }
        }

        print_clean_json({cleaner::clean_files(file_paths, dry_run)});
        return 0;
    }

    print_usage();
    return 1;
}
