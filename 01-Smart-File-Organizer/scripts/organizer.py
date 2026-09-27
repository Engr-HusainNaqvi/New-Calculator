"""
Smart File Organizer

Stage 3: scan the input folder and show which folder each file would go to.
Nothing is moved or changed.
"""

from pathlib import Path

# Folders are found relative to this script, so it works no matter
# which folder you run it from.
PROJECT_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = PROJECT_DIR / "input"

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


def format_size(size_in_bytes):
    """Turn a number of bytes into readable text like '120 KB'."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    if size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.0f} KB"
    return f"{size_in_bytes / (1024 * 1024):.1f} MB"


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


def main():
    files = scan_files(INPUT_DIR)

    print(f"Scanning: {INPUT_DIR}")
    print(f"Found {len(files)} file(s)\n")

    print("PROPOSED CLASSIFICATION (nothing is moved)\n")
    print(f"{'FILENAME':<20} {'EXTENSION':<10} {'SIZE':>10}   DESTINATION")
    print("-" * 58)
    for file in files:
        # file.suffix is ".pdf" -> remove the dot and make it uppercase
        extension = file.suffix.lstrip(".").upper() or "(none)"
        size = format_size(file.stat().st_size)
        destination = classify(file)
        print(f"{file.name:<20} {extension:<10} {size:>10}   {destination}/")


# This line means: only run main() when the file is run directly,
# not when another script imports it (useful later for testing).
if __name__ == "__main__":
    main()
