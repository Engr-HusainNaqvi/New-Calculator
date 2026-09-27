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
from pathlib import Path

# Folders are found relative to this script, so it works no matter
# which folder you run it from.
PROJECT_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = PROJECT_DIR / "input"
OUTPUT_DIR = PROJECT_DIR / "output"

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
    args = parse_arguments()
    dry_run = args.dry_run

    files = scan_files(INPUT_DIR)

    if dry_run:
        print("DRY RUN - nothing will be moved\n")
    print(f"Scanning: {INPUT_DIR}")
    print(f"Found {len(files)} file(s)\n")

    if not dry_run:
        create_category_folders()

    # In a dry run we say what *would* happen
    action = "WOULD MOVE" if dry_run else "MOVED"

    renamed = 0
    unknown_files = []  # remember unsupported files for the summary
    for file in files:
        folder_name = classify(file)
        destination = organize_file(file, dry_run)

        if destination.name == file.name:
            result = action
        else:
            result = f"{action} (renamed to {destination.name})"
            renamed += 1

        # Make unsupported file types stand out instead of hiding them
        if folder_name == UNKNOWN_CATEGORY:
            extension = file.suffix or "no extension"
            result += f"  [unknown type: {extension}]"
            unknown_files.append(file.name)

        print(f"{file.name:<20} -> {folder_name + '/':<12} {result}")

    if dry_run:
        print(f"\nDry run finished: {len(files)} file(s) would be moved "
              f"({renamed} renamed). Run without --dry-run to organize.")
    else:
        print(f"\nDone: {len(files)} moved ({renamed} renamed to avoid duplicates).")

    if unknown_files:
        print(f"\nNote: {len(unknown_files)} file(s) with an unsupported type "
              f"{'would go' if dry_run else 'went'} to {UNKNOWN_CATEGORY}/:")
        for name in unknown_files:
            print(f"  - {name}")


# This line means: only run main() when the file is run directly,
# not when another script imports it (useful later for testing).
if __name__ == "__main__":
    main()
