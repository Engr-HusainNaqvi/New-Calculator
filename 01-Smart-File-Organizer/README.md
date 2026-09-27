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
- [ ] Stage 2: Scan files
- [ ] Stage 3: File classification
- [ ] Stage 4: Organize files
- [ ] Stage 5: Duplicate protection
- [ ] Stage 6: Dry run mode
- [ ] Stage 7: Unknown files
- [ ] Stage 8: Activity log
- [ ] Stage 9: Error handling
- [ ] Stage 10: Testing

## Safety rules

- The tool only works inside this project folder.
- It never deletes files.
- It never overwrites files. If a name is already taken, it renames the new file (`report_1.pdf`).
