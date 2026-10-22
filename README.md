# File Organizer

**Veda Technology: Python Programming Track · Level 1 · Task 22 (Day 22)**

A Python script that **scans a folder and automatically organizes files into sub-folders based on their extensions**, with safety features so nothing is lost.

## Files
| File | Purpose |
|---|---|
| `file_organizer.py` | The file organizer script |
| `create_test_directory.py` | Builds a safe test directory full of tiny dummy files |
| `before_structure.txt` | Test directory structure **before** organizing |
| `after_structure.txt` | Test directory structure **after** organizing |
| `REPORT.pdf` | Task report |

## Features
- Uses `pathlib` for readable path handling and `shutil.move` to move files
- Sorts files into `Images`, `Documents`, `Audio`, `Videos`, `Archives`, `Code`, and `Others`
- **Duplicate-safe:** an existing file is never overwritten. `photo1.jpg` becomes `photo1_1.jpg`, then `photo1_2.jpg`, and so on
- **Dry-run mode** to preview every move before doing it
- **Undo** to put every file back where it came from
- Asks for confirmation before moving anything
- Refuses to run on a drive root or your home folder
- Leaves existing sub-folders, hidden files, and the script itself alone
- Extension matching is case-insensitive (`.JPG` works); files with no extension go to `Others`

## Requirements
Python 3.6+ (standard library only: `pathlib`, `shutil`, `argparse`, `json`)

## How to Run (safe test first)
**Do not test on important personal files.** Use the test directory:

```bash
python create_test_directory.py                       # 1. create test_directory with dummy files
python file_organizer.py test_directory --dry-run     # 2. preview (nothing moves)
python file_organizer.py test_directory               # 3. organize (asks y/n)
python file_organizer.py test_directory --undo        # 4. put everything back
```

Run `create_test_directory.py` again at any time to reset the test directory.

| Option | Meaning |
|---|---|
| `--dry-run` | Show what would happen, move nothing |
| `--undo` | Restore files from the last run |
| `--yes` | Skip the confirmation question |

## File Categories
| Folder | Extensions |
|---|---|
| Images | .jpg .jpeg .png .gif .bmp .svg .webp |
| Documents | .pdf .doc .docx .txt .rtf .odt .xls .xlsx .csv .ppt .pptx |
| Audio | .mp3 .wav .aac .flac .ogg |
| Videos | .mp4 .mkv .avi .mov .wmv |
| Archives | .zip .rar .7z .tar .gz |
| Code | .py .js .html .css .java .c .cpp .json .xml |
| Others | everything else, including files with no extension |

Categories live in the `CATEGORIES` dictionary at the top of the script, so adding an extension is a one-line change.

## Before and After
The test directory has 23 files to organize, 1 hidden file, 1 sub-folder (`old_stuff`), and two files already inside `Images` and `Documents` that force duplicate-name handling. Full trees are in `before_structure.txt` and `after_structure.txt`.

**Before (top of the tree)**
```
test_directory/
|-- Documents/
|   `-- report.pdf
|-- Images/
|   `-- photo1.jpg
|-- old_stuff/
|   `-- old_notes.txt
|-- .hidden_config
|-- archive.tar.gz
|-- backup.zip
|-- ... (20 more files in the main folder)
```

**After (top of the tree)**
```
test_directory/
|-- Archives/
|   |-- archive.tar.gz
|   `-- backup.zip
|-- Audio/
|-- Code/
|-- Documents/
|   |-- report.pdf
|   |-- report_1.pdf      <- duplicate name handled safely
|   `-- ...
|-- Images/
|   |-- photo1.jpg
|   |-- photo1_1.jpg      <- duplicate name handled safely
|   `-- ...
|-- old_stuff/            <- untouched
```

## Sample Output
```
SUMMARY
  Archives  : 2 file(s)
  Audio     : 2 file(s)
  Code      : 4 file(s)
  Documents : 6 file(s)
  Images    : 4 file(s)
  Others    : 3 file(s)
  Videos    : 2 file(s)
  Moved: 23 | Duplicates renamed: 2 | Skipped: 4
    skipped .hidden_config: hidden file
    skipped Documents: folder (left untouched)
    skipped Images: folder (left untouched)
    skipped old_stuff: folder (left untouched)
```

## Safety Notes
- Nothing is ever deleted or overwritten. Files are only moved or renamed.
- A hidden `.organizer_log.json` file records every move so `--undo` can reverse it. It is removed after a successful undo.
- Undo only removes category folders that the script itself created, and only if they are empty.

## Author
Nabila, Veda Technology Intern