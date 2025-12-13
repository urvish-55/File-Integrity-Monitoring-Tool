# File Integrity Checker (CODTECH Internship – Task 1)

This tool monitors changes in files by calculating and comparing hash values
to ensure file integrity. It is implemented in Python using the built-in
`hashlib` library.

## Features
- Create a baseline of SHA-256 hashes for all files in a folder
- Detect added, removed, modified, and unchanged files
- Simple command-line interface
- JSON-based baseline for easy storage and review

## Usage
python file_integrity_checker.py init <path to folder> baseline.json
python file_integrity_checker.py check <path to folder> baseline.json