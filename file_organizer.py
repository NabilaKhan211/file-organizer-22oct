"""File Organizer.

Scans a folder and moves its files into sub-folders based on file extension:
    Images, Documents, Audio, Videos, Archives, Code, Others

Safety features:
    * --dry-run   shows what WOULD happen without moving anything
    * duplicate filenames are never overwritten (photo.jpg -> photo_1.jpg)
    * asks for confirmation before moving (skip with --yes)
    * refuses to run on a drive root or your home folder
    * every move is logged (in a hidden .organizer_log.json), so --undo can put files back

Usage:
    python file_organizer.py FOLDER [--dry-run] [--undo] [--yes]
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

# extension -> category folder
CATEGORIES = {
    "Images":    {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".csv", ".ppt", ".pptx"},
    "Audio":     {".mp3", ".wav", ".aac", ".flac", ".ogg"},
    "Videos":    {".mp4", ".mkv", ".avi", ".mov", ".wmv"},
    "Archives":  {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code":      {".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".json", ".xml"},
}
OTHERS = "Others"
LOG_NAME = ".organizer_log.json"  # hidden, so it is never organized itself


# ---------- Core functions ----------
def get_category(path):
    """Return the category folder name for a file, based on its extension."""
    extension = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category
    return OTHERS


def unique_destination(destination):
    """Return a path that does not exist yet: name.ext, name_1.ext, name_2.ext ..."""
    if not destination.exists():
        return destination
    counter = 1
    while True:
        candidate = destination.with_name(f"{destination.stem}_{counter}{destination.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def plan_moves(folder):
    """Decide what to move. Returns (moves, skipped); nothing is changed on disk.

    moves   : list of (source, destination) pairs
    skipped : list of (name, reason)
    """
    moves, skipped = [], []
    this_script = Path(__file__).resolve()
    for item in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
        if item.is_dir():
            skipped.append((item.name, "folder (left untouched)"))
        elif item.name.startswith("."):
            skipped.append((item.name, "hidden file"))
        elif item.resolve() == this_script:
            skipped.append((item.name, "the organizer script itself"))
        else:
            destination = unique_destination(folder / get_category(item) / item.name)
            moves.append((item, destination))
    return moves, skipped


def organize(folder, dry_run=False):
    """Perform (or just preview) the moves. Returns (moves, skipped, renamed_count)."""
    moves, skipped = plan_moves(folder)
    log, created, renamed = [], [], 0
    for source, destination in moves:
        if destination.name != source.name:
            renamed += 1
        if not dry_run:
            if not destination.parent.exists():
                destination.parent.mkdir()
                created.append(destination.parent.name)
            shutil.move(str(source), str(destination))
            log.append({"from": str(source), "to": str(destination)})
    if log:
        with open(folder / LOG_NAME, "w", encoding="utf-8") as file:
            json.dump({"moves": log, "created_folders": created}, file, indent=2)
    return moves, skipped, renamed


def undo(folder):
    """Move files back to where they came from, using the log. Returns (restored, problems)."""
    log_file = folder / LOG_NAME
    if not log_file.exists():
        return 0, ["No log found. Nothing to undo."]
    with open(log_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    restored, problems = 0, []
    for entry in reversed(data["moves"]):
        source, current = Path(entry["from"]), Path(entry["to"])
        if not current.exists():
            problems.append(f"{current.name}: no longer at {current.parent.name}/, skipped")
        elif source.exists():
            problems.append(f"{source.name}: a file with that name already exists, skipped")
        else:
            shutil.move(str(current), str(source))
            restored += 1
    for name in data["created_folders"]:             # remove only folders the script created
        category_dir = folder / name
        if category_dir.is_dir() and not any(category_dir.iterdir()):
            category_dir.rmdir()
    if not problems:
        log_file.unlink()
    return restored, problems


# ---------- Display helpers ----------
def tree_lines(folder, prefix=""):
    """Return the folder structure as a list of text lines (ASCII tree)."""
    entries = sorted((p for p in folder.iterdir() if p.name != LOG_NAME),   # the log file is hidden from the display
                     key=lambda p: (not p.is_dir(), p.name.lower()))
    lines = []
    for index, entry in enumerate(entries):
        last = index == len(entries) - 1
        lines.append(f"{prefix}{'`-- ' if last else '|-- '}{entry.name}{'/' if entry.is_dir() else ''}")
        if entry.is_dir():
            lines += tree_lines(entry, prefix + ("    " if last else "|   "))
    return lines


def show_tree(folder, title):
    print(f"\n{title}")
    print(f"{folder.name}/")
    for line in tree_lines(folder):
        print(line)


def is_unsafe(folder):
    """Refuse drive roots and the home folder to avoid reorganizing important files."""
    return folder == folder.parent or folder == Path.home().resolve()


def main():
    parser = argparse.ArgumentParser(description="Organize files into folders by extension.")
    parser.add_argument("folder", nargs="?", help="folder to organize")
    parser.add_argument("--dry-run", action="store_true", help="preview only, move nothing")
    parser.add_argument("--undo", action="store_true", help="restore files from the last run")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation question")
    args = parser.parse_args()

    raw = args.folder or input("Enter the folder to organize: ").strip().strip('"')
    folder = Path(raw).expanduser().resolve()
    if not folder.is_dir():
        print(f"Error: '{raw}' is not a folder.")
        return 1
    if is_unsafe(folder):
        print("Error: refusing to organize a drive root or your home folder. Choose a test folder.")
        return 1

    if args.undo:
        restored, problems = undo(folder)
        print(f"Restored {restored} file(s).")
        for problem in problems:
            print("  - " + problem)
        return 0

    moves, skipped = plan_moves(folder)
    if not moves:
        print("No files to organize. The folder is already tidy.")
        return 0

    show_tree(folder, "BEFORE:")
    if args.dry_run:
        print("\nDRY RUN (nothing will be moved). Planned moves:")
        for source, destination in moves:
            print(f"  {source.name:<20} -> {destination.parent.name}/{destination.name}")
        print(f"\n{len(moves)} file(s) would be moved, {len(skipped)} item(s) skipped.")
        return 0

    if not args.yes:
        answer = input(f"\nMove {len(moves)} file(s) inside '{folder.name}'? (y/n): ").strip().lower()
        if answer != "y":
            print("Cancelled. Nothing was changed.")
            return 0

    moves, skipped, renamed = organize(folder)
    show_tree(folder, "AFTER:")

    counts = {}
    for _, destination in moves:
        counts[destination.parent.name] = counts.get(destination.parent.name, 0) + 1
    print("\nSUMMARY")
    for category, count in sorted(counts.items()):
        print(f"  {category:<10}: {count} file(s)")
    print(f"  Moved: {len(moves)} | Duplicates renamed: {renamed} | Skipped: {len(skipped)}")
    for name, reason in skipped:
        print(f"    skipped {name}: {reason}")
    print("\nTo undo, run:  python file_organizer.py " + f'"{folder}" --undo')
    return 0


if __name__ == "__main__":
    sys.exit(main())