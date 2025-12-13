#!/usr/bin/env python3
"""
Simple File Integrity Checker
Author: Urvish Kharate
Internship: CODTECH IT SOLUTIONS

Features:
- Create a baseline of file hashes for a folder
- Compare current state of files with the saved baseline
- Uses SHA-256 by default (secure & standard)

Usage:
    python file_integrity_checker.py init  <folder_path> baseline.json
    python file_integrity_checker.py check <folder_path> baseline.json
"""

import hashlib
import os
import json
import time
import argparse


def compute_file_hash(path, algo="sha256", chunk_size=65536):
    """
    Calculate the hash of a file using the given algorithm.
    Default algorithm = sha256.

    :param path: Path to file
    :param algo: Hash algorithm name (e.g., 'sha256', 'sha1', 'md5')
    :param chunk_size: How many bytes to read at once
    :return: Hex digest string of the hash
    """
    hasher = hashlib.new(algo)

    with open(path, "rb") as f:
        # Read file in chunks so large files don't use too much RAM
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def scan_directory(root_folder, algo="sha256"):
    """
    Walk through a directory and hash all files.

    :param root_folder: Folder to scan
    :param algo: Hash algorithm
    :return: Dictionary {relative_path: {hash, size, mtime}}
    """
    file_info = {}

    for dirpath, _, filenames in os.walk(root_folder):
        for name in filenames:
            full_path = os.path.join(dirpath, name)

            # Relative path to keep JSON portable
            rel_path = os.path.relpath(full_path, root_folder)

            try:
                file_hash = compute_file_hash(full_path, algo)
                size = os.path.getsize(full_path)
                mtime = os.path.getmtime(full_path)

                file_info[rel_path] = {
                    "hash": file_hash,
                    "size": size,
                    "mtime": mtime,
                }
            except (PermissionError, OSError) as e:
                print(f"[WARN] Could not read '{full_path}': {e}")

    return file_info


def save_baseline(baseline_path, root_folder, algo="sha256"):
    """
    Create and save a baseline snapshot as JSON.
    """
    root_folder = os.path.abspath(root_folder)
    print(f"[+] Scanning folder: {root_folder} using {algo} ...")

    files = scan_directory(root_folder, algo)

    snapshot = {
        "root_folder": root_folder,
        "hash_algorithm": algo,
        "created_at": time.time(),
        "files": files,
    }

    with open(baseline_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=4)

    print(f"[+] Baseline saved to '{baseline_path}' with {len(files)} files.")


def load_baseline(baseline_path):
    """
    Load baseline JSON file.
    """
    with open(baseline_path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_with_baseline(root_folder, baseline):
    """
    Compare current folder state with stored baseline.

    :param root_folder: Folder to scan now
    :param baseline: Loaded JSON baseline dict
    :return: Report dict with added/removed/modified/unchanged
    """
    algo = baseline["hash_algorithm"]
    old_files = baseline["files"]

    print(f"[+] Scanning current state of '{root_folder}' using {algo} ...")
    new_files = scan_directory(root_folder, algo)

    old_set = set(old_files.keys())
    new_set = set(new_files.keys())

    added = sorted(list(new_set - old_set))
    removed = sorted(list(old_set - new_set))

    modified = []
    unchanged = []

    for rel_path in new_set & old_set:
        if new_files[rel_path]["hash"] != old_files[rel_path]["hash"]:
            modified.append(rel_path)
        else:
            unchanged.append(rel_path)

    return {
        "added": added,
        "removed": removed,
        "modified": sorted(modified),
        "unchanged": sorted(unchanged),
    }


def print_report(report):
    """
    Pretty-print comparison results.
    """

    def print_section(title, items):
        print(f"\n=== {title} ({len(items)}) ===")
        if not items:
            print("  (none)")
        else:
            for item in items:
                print(f"  - {item}")

    print_section("ADDED FILES", report["added"])
    print_section("REMOVED FILES", report["removed"])
    print_section("MODIFIED FILES", report["modified"])
    print_section("UNCHANGED FILES", report["unchanged"])


def main():
    parser = argparse.ArgumentParser(
        description="File Integrity Checker - CODTECH Internship Task 1"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- init command ---
    init_parser = subparsers.add_parser(
        "init", help="Create a new baseline for a folder"
    )
    init_parser.add_argument("folder", help="Folder to scan")
    init_parser.add_argument("baseline", help="Output JSON file (baseline)")
    init_parser.add_argument(
        "--algo",
        default="sha256",
        help="Hash algorithm (default: sha256, others: sha1, md5, etc.)",
    )

    # --- check command ---
    check_parser = subparsers.add_parser(
        "check", help="Check folder against an existing baseline"
    )
    check_parser.add_argument("folder", help="Folder to scan")
    check_parser.add_argument("baseline", help="Existing baseline JSON file")

    args = parser.parse_args()

    if args.command == "init":
        save_baseline(args.baseline, args.folder, args.algo)
    elif args.command == "check":
        baseline = load_baseline(args.baseline)
        report = compare_with_baseline(args.folder, baseline)
        print_report(report)


if __name__ == "__main__":
    main()
