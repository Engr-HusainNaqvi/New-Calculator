"""
Smart File Organizer

Stage 4: move each file from the input folder into a folder in output
that matches its type (PDFs, Images, Excel, ...). Existing files are
never overwritten.
"""

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
    """Create output/PDFs, output/Images, ... if they don't exist yet."""
    # set() removes duplicates: "Images" appears 3 times in CATEGORIES
    for folder_name in sorted(set(CATEGORIES.values())):
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


def organize_file(file):
    """Move one file into its category folder. Returns the new path."""
    destination_folder = OUTPUT_DIR / classify(file)
    destination_folder.mkdir(parents=True, exist_ok=True)

    # Never overwrite: pick a free name (renaming if necessary)
    destination = unique_destination(destination_folder, file.name)

    shutil.move(str(file), str(destination))
    return destination


def main():
    files = scan_files(INPUT_DIR)

    print(f"Scanning: {INPUT_DIR}")
    print(f"Found {len(files)} file(s)\n")

    create_category_folders()

    renamed = 0
    for file in files:
        folder_name = classify(file)
        destination = organize_file(file)

        if destination.name == file.name:
            result = "MOVED"
        else:
            result = f"MOVED (renamed to {destination.name})"
            renamed += 1

        print(f"{file.name:<20} -> {folder_name + '/':<12} {result}")

    print(f"\nDone: {len(files)} moved ({renamed} renamed to avoid duplicates).")


# This line means: only run main() when the file is run directly,
# not when another script imports it (useful later for testing).
if __name__ == "__main__":
    main()
