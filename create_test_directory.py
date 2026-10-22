"""Creates a safe test directory full of tiny dummy files for the File Organizer.

Usage:
    python create_test_directory.py            (creates ./test_directory)
    python create_test_directory.py my_folder  (creates ./my_folder)

Run it again at any time to reset the test directory to its starting state.
"""
import shutil
import sys
from pathlib import Path

TOP_LEVEL_FILES = [
    "photo1.jpg", "photo2.png", "vacation.JPG", "logo.svg",                  # Images (.JPG tests upper case)
    "report.pdf", "notes.txt", "resume.docx", "budget.xlsx", "slides.pptx", "data.csv",   # Documents
    "song.mp3", "podcast.wav",                                               # Audio
    "movie.mp4", "clip.mkv",                                                 # Videos
    "backup.zip", "archive.tar.gz",                                          # Archives
    "script.py", "index.html", "style.css", "config.json",                   # Code
    "setup.exe", "README", "unknown.xyz",                                    # Others (README has no extension)
    ".hidden_config",                                                        # hidden: must be skipped
]
# Files that already exist in category folders: they force duplicate-name handling
EXISTING = {"Images": ["photo1.jpg"], "Documents": ["report.pdf"]}
# A sub-folder that must be left untouched
SUBFOLDER = {"old_stuff": ["old_notes.txt"]}


def make_file(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"dummy content for {path.name}\n", encoding="utf-8")


def main():
    target = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "test_directory").resolve()
    if target.exists():
        shutil.rmtree(target)
    for name in TOP_LEVEL_FILES:
        make_file(target / name)
    for folder, names in {**EXISTING, **SUBFOLDER}.items():
        for name in names:
            make_file(target / folder / name)
    print(f"Test directory created: {target}")
    print(f"  {len(TOP_LEVEL_FILES)} files at the top level (1 hidden), "
          f"{sum(len(v) for v in EXISTING.values())} pre-existing files in category folders (duplicate test), "
          f"1 sub-folder (must stay untouched)")


if __name__ == "__main__":
    main()