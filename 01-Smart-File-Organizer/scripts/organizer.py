"""
Smart File Organizer

Moves each file from the input folder into a folder in output that
matches its type (PDFs, Images, Excel, ...). Existing files are never
overwritten: a clashing name gets a number (report_1.pdf).

Usage:
    python scripts/organizer.py --dry-run   # preview only, nothing moves
    python scripts/organizer.py             # organize for real
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Folders are found relative to this script, so it works no matter
# which folder you run it from.
PROJECT_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = PROJECT_DIR / "input"
OUTPUT_DIR = PROJECT_DIR / "output"
LOG_FILE = OUTPUT_DIR / "organization_log.txt"

# Classification rules: extension (lowercase, no dot) -> destination folder.
# To support a new file type, just add a line here.
CATEGORIES = {
    "pdf": "PDFs",
    "jpg": "Images",
    "jpeg": "Images",
    "png": "Images",
    "xls": "Excel",
    "xlsx": "Excel",
    "doc": "Word",
    "docx": "Word",
    "ppt": "PowerPoint",
    "pptx": "PowerPoint",
    "txt": "Text",
}

# Where files go when their extension is not in CATEGORIES.
UNKNOWN_CATEGORY = "Other"


def scan_files(folder):
    """Return a sorted list of the files in a folder (sub-folders are skipped)."""
    files = []
    for item in folder.iterdir():
        # Skip folders and hidden files such as .gitkeep
        if item.is_file() and not item.name.startswith("."):
            files.append(item)
    return sorted(files)


def find_subfolders(folder):
    """Return the names of sub-folders (they are not organized, only reported)."""
    subfolders = []
    for item in folder.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            subfolders.append(item.name)
    return sorted(subfolders)


def classify(file):
    """Return the destination folder name for a file, e.g. 'PDFs'."""
    # .lower() makes "PHOTO.JPG" and "photo.jpg" follow the same rule
    extension = file.suffix.lstrip(".").lower()
    # .get() returns UNKNOWN_CATEGORY if the extension is not in the table
    return CATEGORIES.get(extension, UNKNOWN_CATEGORY)


def create_category_folders():
    """Create output/PDFs, output/Images, ..., output/Other if missing."""
    # set() removes duplicates: "Images" appears 3 times in CATEGORIES
    folder_names = set(CATEGORIES.values())
    folder_names.add(UNKNOWN_CATEGORY)
    for folder_name in sorted(folder_names):
        # exist_ok=True: no error if the folder is already there
        (OUTPUT_DIR / folder_name).mkdir(parents=True, exist_ok=True)


def unique_destination(folder, filename):
    """
    Return a path in `folder` that is not taken yet.

    report.pdf -> report.pdf, or report_1.pdf, report_2.pdf, ... if taken.
    """
    candidate = folder / filename
    stem = candidate.stem      # "report"
    suffix = candidate.suffix  # ".pdf"
    counter = 1

    # Keep trying the next number until we find a free name
    while candidate.exists():
        candidate = folder / f"{stem}_{counter}{suffix}"
        counter += 1

    return candidate


def organize_file(file, dry_run=False):
    """
    Move one file into its category folder. Returns the new path.

    With dry_run=True nothing is created or moved; we only work out
    where the file *would* go.
    """
    destination_folder = OUTPUT_DIR / classify(file)

    # Never overwrite: pick a free name (renaming if necessary)
    destination = unique_destination(destination_folder, file.name)

    if not dry_run:
        destination_folder.mkdir(parents=True, exist_ok=True)
        shutil.move(str(file), str(destination))

    return destination


def write_log(filename, destination, action):
    """
    Add one line to the activity log, for example:
    2026-09-27 14:30:05 | report.pdf | PDFs/ | MOVED
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} | {filename} | {destination} | {action}\n"

    # "a" = append: add to the end of the file, never erase what's there.
    # The file is created automatically the first time.
    # Returns True if the line was written, False if the log is unavailable.
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            log.write(line)
        return True
    except OSError:
        return False


def describe_error(error):
    """Turn a Python error into a short message a user can understand."""
    if isinstance(error, PermissionError):
        return "permission denied (is the file open in another program?)"
    if isinstance(error, FileNotFoundError):
        return "file not found (was it moved or deleted during the run?)"
    if isinstance(error, FileExistsError):
        return f"a file is in the way where a folder should be: {error.filename}"
    # Any other file-system problem: use the system's own description
    return error.strerror or str(error)


def parse_arguments():
    """Read the options typed after the script name."""
    parser = argparse.ArgumentParser(
        description="Organize files in the input folder by file type."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",  # True if --dry-run is typed, else False
        help="show what would happen without moving anything",
    )
    return parser.parse_args()


def main():
    """Run the organizer. Returns an exit code: 0 = success, 1 = problems."""
    args = parse_arguments()
    dry_run = args.dry_run

    if dry_run:
        print("DRY RUN - nothing will be moved\n")
    print(f"Scanning: {INPUT_DIR}")

    # --- Fatal problems: we can't do anything, so stop with a clear message
    if not INPUT_DIR.exists():
        print(f"ERROR: the input folder does not exist: {INPUT_DIR}")
        print("Create it and put the files you want organized inside.")
        return 1
    if not INPUT_DIR.is_dir():
        print(f"ERROR: 'input' is a file, not a folder: {INPUT_DIR}")
        return 1
    try:
        files = scan_files(INPUT_DIR)
        subfolders = find_subfolders(INPUT_DIR)
    except OSError as error:
        print(f"ERROR: cannot read the input folder: {describe_error(error)}")
        return 1

    print(f"Found {len(files)} file(s)\n")

    # Don't ignore sub-folders silently: say they were left where they are
    if subfolders:
        print(f"Note: {len(subfolders)} sub-folder(s) left in place "
              f"(only files are organized): {', '.join(subfolders)}\n")

    if not files:
        print("Nothing to organize: there are no files in the input folder.")
        return 0

    if not dry_run:
        try:
            create_category_folders()
        except OSError as error:
            print(f"ERROR: cannot create the output folders in {OUTPUT_DIR}: "
                  f"{describe_error(error)}")
            print("No files were moved.")
            return 1

    # In a dry run we say what *would* happen
    action = "WOULD MOVE" if dry_run else "MOVED"

    renamed = 0
    errors = 0
    log_ok = True
    unknown_files = []  # remember unsupported files for the summary
    for file in files:
        folder_name = classify(file)

        # --- Per-file problems: report and log them, then carry on
        try:
            destination = organize_file(file, dry_run)
        except OSError as error:
            errors += 1
            result = f"ERROR: {describe_error(error)}"
            print(f"{file.name:<20} -> {folder_name + '/':<12} {result}")
            if not dry_run:
                log_ok = write_log(file.name, f"{folder_name}/", result) and log_ok
            continue  # skip to the next file

        if destination.name == file.name:
            result = action
        else:
            result = f"{action} (renamed to {destination.name})"
            renamed += 1

        # Make unsupported file types stand out instead of hiding them
        if folder_name == UNKNOWN_CATEGORY:
            extension = file.suffix or "no extension"
            result += f" [unknown type: {extension}]"
            unknown_files.append(file.name)

        print(f"{file.name:<20} -> {folder_name + '/':<12} {result}")

        # Record real moves only: a dry run must not change anything
        if not dry_run:
            log_ok = write_log(file.name, f"{folder_name}/", result) and log_ok

    ok_count = len(files) - errors
    if dry_run:
        print(f"\nDry run finished: {ok_count} file(s) would be moved "
              f"({renamed} renamed). Run without --dry-run to organize.")
    else:
        print(f"\nDone: {ok_count} moved ({renamed} renamed to avoid duplicates).")

    if unknown_files:
        print(f"\nNote: {len(unknown_files)} file(s) with an unsupported type "
              f"{'would go' if dry_run else 'went'} to {UNKNOWN_CATEGORY}/:")
        for name in unknown_files:
            print(f"  - {name}")

    if errors:
        print(f"\nWARNING: {errors} file(s) could not be moved and were left "
              f"in the input folder. See the messages above.")
    if not log_ok:
        print(f"\nWARNING: could not write to the log file: {LOG_FILE}")

    return 1 if errors or not log_ok else 0


# This line means: only run main() when the file is run directly,
# not when another script imports it (useful later for testing).
# sys.exit() passes main()'s exit code (0 or 1) back to the system.
if __name__ == "__main__":
    sys.exit(main())
