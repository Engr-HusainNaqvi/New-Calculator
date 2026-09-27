# Smart File Organizer

A simple Python tool that sorts the files in the `input` folder into
subfolders of `output` by file type (PDFs, Images, Excel, Word, and so on).

This is a learning project, built in small stages with Claude Code.

## Folder structure

```text
01-Smart-File-Organizer/
├── input/      Put the files you want organized here
├── output/     Organized files and the activity log end up here
├── scripts/    The Python code (organizer.py)
└── README.md   This file
```

## Requirements

- Python 3.8 or newer
- No extra packages: the tool uses only Python's standard library

## Status

- [x] Stage 1: Project setup
- [x] Stage 2: Scan files
- [x] Stage 3: File classification
- [x] Stage 4: Organize files
- [x] Stage 5: Duplicate protection
- [x] Stage 6: Dry run mode
- [ ] Stage 7: Unknown files
- [ ] Stage 8: Activity log
- [ ] Stage 9: Error handling
- [ ] Stage 10: Testing

## Classification rules

| Extension        | Folder       |
|------------------|--------------|
| PDF              | PDFs/        |
| JPG, JPEG, PNG   | Images/      |
| XLS, XLSX        | Excel/       |
| DOC, DOCX        | Word/        |
| PPT, PPTX        | PowerPoint/  |
| TXT              | Text/        |
| anything else    | Other/       |

Extensions are matched case-insensitively (`PHOTO.JPG` counts as JPG).
To add a new type, add a line to `CATEGORIES` in `scripts/organizer.py`.

## Safety rules

- The tool only works inside this project folder.
- It never deletes files.
- It never overwrites files. If a name is already taken in the destination, the new file is renamed: `report.pdf`, `report_1.pdf`, `report_2.pdf`, ...

## How to run

From the `01-Smart-File-Organizer` folder:

```bash
# 1. Preview: shows where every file would go, moves nothing
python scripts/organizer.py --dry-run

# 2. Organize for real
python scripts/organizer.py

# Show all options
python scripts/organizer.py --help
```

(Use `python3` instead of `python` on macOS/Linux.)

Tip: always do a dry run first.
