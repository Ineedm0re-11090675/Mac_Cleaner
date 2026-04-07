from __future__ import annotations

import argparse
import json

from bridge import CleanerBridge


def main() -> None:
    parser = argparse.ArgumentParser(description="Python interface for the macOS cleaner core.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan categories")
    scan_parser.add_argument("categories", nargs="*", help="Optional category keys")

    clean_parser = subparsers.add_parser("clean", help="Clean categories")
    clean_parser.add_argument("categories", nargs="+", help="Category keys")
    clean_parser.add_argument("--execute", action="store_true", help="Actually delete files")

    args = parser.parse_args()
    bridge = CleanerBridge()

    if args.command == "scan":
        result = bridge.scan(args.categories)
    else:
        result = bridge.clean(args.categories, dry_run=not args.execute)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
