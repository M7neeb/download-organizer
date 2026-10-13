#!/usr/bin/env python3
"""
Download File Organizer - the engine.
=====================================

This module does the actual work: look at files, decide where each one goes,
move them, and remember what it did so you can undo it.

The interesting bit lives in `classify()`, which decides a file's destination
by checking the patterns we worked out in patterns.py. Order of preference:

  1. Rules you accepted (from a suggestion) - these always win.
  2. Automatic signals - things that are obviously their own folder.
  3. The file's real type from its bytes.
  4. The file extension.

Command line:
    python organizer.py                  sort Downloads once
    python organizer.py --dry-run        show what would happen
    python organizer.py --watch 30       re-scan every 30 seconds
    python organizer.py --suggest        list the patterns it has noticed
    python organizer.py --undo           put back the last run
"""

import argparse
import shutil
import sys
import time
from pathlib import Path

import config
import history
import patterns

# Files we never touch.
JUNK_NAMES = {"thumbs.db", "desktop.ini", ".ds_store", "config.json",
              "history.json"}

# Endings that mean "this download is not finished".
PARTIAL_SUFFIXES = {".part", ".crdownload", ".tmp", ".download", ".opdownload"}

# A zip that is really something else, judged by its extension.
ZIP_KIND = {
    "docx": "Documents", "xlsx": "Documents", "pptx": "Documents",
    "odt": "Documents", "ods": "Documents",
    "epub": "eBooks",
    "apk": "Android", "aab": "Android", "xapk": "Android",
    "jar": "Code",
}


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------
def build_extension_lookup(categories: dict) -> dict:
    """{"Images": ["jpg", ...]} -> {"jpg": "Images", ...}."""
    lookup = {}
    for folder, extensions in categories.items():
        for ext in extensions:
            lookup[str(ext).lower().lstrip(".")] = folder
    return lookup


def looks_like_download(entry: Path, min_age: float):
    """Return (ok, reason). ok=False means leave the file alone."""
    if entry.name.lower() in JUNK_NAMES:
        return False, "system file"
    if entry.suffix.lower() in PARTIAL_SUFFIXES:
        return False, "still downloading"
    try:
        age = time.time() - entry.stat().st_mtime
    except OSError:
        return True, ""
    if age < min_age:
        return False, f"changed {age:.0f}s ago"
    return True, ""


def unique_destination(dest_dir: Path, name: str) -> Path:
    """Never overwrite - bump to 'name (1).ext' if needed."""
    dest = dest_dir / name
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    counter = 1
    while True:
        candidate = dest_dir / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


# --------------------------------------------------------------------------
# Reading a folder
# --------------------------------------------------------------------------
def read_folder(source: Path, cfg: dict):
    """Analyse every plausible downloaded file in `source`.

    Returns (files, skipped) where files is [(path, info), ...].
    """
    min_age = cfg.get("min_age_seconds", 5)
    files, skipped = [], []

    for entry in sorted(source.iterdir()):
        if not entry.is_file():
            continue
        ok, reason = looks_like_download(entry, min_age)
        if not ok:
            if reason != "system file":
                skipped.append((entry.name, reason))
            continue
        try:
            info = patterns.analyze(entry)
        except OSError:
            continue
        files.append((entry, info))

    return files, skipped


# --------------------------------------------------------------------------
# The decision itself
# --------------------------------------------------------------------------
def _best_match(file_signals, mapping):
    """Pick the highest-priority signal present in `mapping`."""
    best, best_rank = None, -1
    for signal in file_signals:
        if signal in mapping:
            rank = patterns.SIGNAL_PRIORITY.get(signal.split(":", 1)[0], 0)
            if rank > best_rank:
                best, best_rank = signal, rank
    return best


def _pick_version(file_signals):
    """The version number to use as a subfolder, if there is one."""
    versions = sorted(s.split(":", 1)[1] for s in file_signals
                      if s.startswith("version:"))
    return versions[-1] if versions else None


def classify(path: Path, info: dict, cfg: dict, ext_lookup: dict) -> str:
    """Where should this file go? Returns a folder (maybe nested)."""
    sigs = patterns.signals(info)

    # 1. A rule you accepted for a suggestion.
    rule_map = {rule["match"]: rule["folder"] for rule in cfg.get("rules", [])
                if "match" in rule and "folder" in rule}
    matched = _best_match(sigs, rule_map)
    folder = rule_map.get(matched) if matched else None

    # 2. A pattern that sorts itself automatically.
    if not folder:
        matched = _best_match(sigs, patterns.AUTO_SIGNALS)
        folder = patterns.AUTO_SIGNALS.get(matched) if matched else None

    # Add a version subfolder for archive-style packages (mods, modpacks...).
    if folder and cfg.get("version_subfolders", True) and matched \
            and matched.startswith("inner:"):
        version = _pick_version(sigs)
        if version:
            folder = f"{folder}/{version}"
    if folder:
        return folder

    # 3. The file's real type.
    file_type = info.get("type")
    if file_type == "archive":
        return ZIP_KIND.get(info.get("ext"), "Archives")
    if file_type in patterns.TYPE_FOLDER:
        return patterns.TYPE_FOLDER[file_type]

    # 4. Plain extension.
    return ext_lookup.get(info.get("ext"), "Other")


# --------------------------------------------------------------------------
# Putting it together
# --------------------------------------------------------------------------
def plan(source: Path, cfg: dict):
    """Work out every move without doing anything.

    Returns (moves, skipped, files):
      moves   - [(source_path, destination_path, folder), ...]
      skipped - [(name, reason), ...]
      files   - [(path, info), ...] used to build the pattern suggestions
    """
    ext_lookup = build_extension_lookup(cfg.get("categories", {}))
    target = resolve_target(cfg, source)

    files, skipped = read_folder(source, cfg)
    moves = []
    for path, info in files:
        folder = classify(path, info, cfg, ext_lookup)
        dest_dir = target / folder
        moves.append((path, unique_destination(dest_dir, path.name), folder))

    return moves, skipped, files


def apply_moves(moves, cfg: dict, target=None):
    """Actually move the files and remember it so it can be undone."""
    done = []
    for src, dst, _folder in moves:
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            done.append((src, dst))
        except OSError as exc:
            print(f"  ! could not move {src.name}: {exc}")

    history.record(done)

    if cfg.get("cleanup_empty_folders", True) and target is not None:
        cleanup_empty_folders(target)
    return done


def cleanup_empty_folders(root):
    """Remove category folders that ended up with nothing in them."""
    if root is None or not Path(root).is_dir():
        return
    for folder in sorted(Path(root).iterdir(), reverse=True):
        if folder.is_dir() and not any(folder.iterdir()):
            try:
                folder.rmdir()
            except OSError:
                pass


# --------------------------------------------------------------------------
# Where things go
# --------------------------------------------------------------------------
def resolve_source(cfg: dict) -> Path:
    if cfg.get("source"):
        return Path(cfg["source"]).expanduser()
    return Path.home() / "Downloads"


def resolve_target(cfg: dict, source: Path) -> Path:
    if cfg.get("target"):
        return Path(cfg["target"]).expanduser()
    return Path(source)


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------
def _print_moves(moves, dry_run):
    groups = {}
    for src, dst, folder in moves:
        groups.setdefault(folder, []).append(src.name)
    for folder in sorted(groups):
        print(f"  {folder}/")
        for name in groups[folder]:
            print(f"      {name}")
    verb = "would move" if dry_run else "moved"
    print(f"\n{verb} {len(moves)} file(s) into {len(groups)} folder(s).")


def main():
    parser = argparse.ArgumentParser(
        description="Organize downloaded files by type and by content.")
    parser.add_argument("source", nargs="?", default=None,
                        help="Folder to organize (default: Downloads)")
    parser.add_argument("--target", default=None,
                        help="Where category folders go (default: source)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would happen, change nothing")
    parser.add_argument("--watch", type=int, metavar="SECONDS",
                        help="Keep re-scanning every SECONDS seconds")
    parser.add_argument("--suggest", action="store_true",
                        help="Show the patterns noticed in the folder")
    parser.add_argument("--accept", metavar="SIGNAL",
                        help="Accept a suggested pattern, e.g. inner:factorio-mod")
    parser.add_argument("--folder", default=None,
                        help="Folder name to use with --accept")
    parser.add_argument("--undo", action="store_true",
                        help="Put back the files moved by the last run")
    args = parser.parse_args()

    cfg = config.load()
    if not config.config_path().exists():
        config.save(cfg)          # create config.json on first run
    if args.source:
        cfg["source"] = args.source
    if args.target:
        cfg["target"] = args.target

    source = resolve_source(cfg)

    if args.undo:
        restored, problems = history.undo_last()
        print(f"Restored {restored} file(s).")
        for problem in problems:
            print(f"  - {problem}")
        return

    if not source.is_dir():
        print(f"Folder not found: {source}")
        sys.exit(1)

    if args.suggest:
        _files, _skipped = read_folder(source, cfg)
        cfg["_ext_lookup"] = build_extension_lookup(cfg.get("categories", {}))
        for suggestion in patterns.suggest(_files, cfg):
            print(f"  {suggestion['count']:>3}  {suggestion['signal']:<28}"
                  f" -> {suggestion['folder']}")
            print(f"       e.g. {', '.join(suggestion['examples'])}")
        return

    if args.accept:
        cfg.setdefault("rules", []).append(
            {"match": args.accept, "folder": args.folder
             or patterns.friendly_folder(args.accept)})
        config.save(cfg)
        print(f"Saved rule: {args.accept} -> "
              f"{cfg['rules'][-1]['folder']}")
        return

    def run_once():
        moves, skipped, _files = plan(source, cfg)
        if not moves:
            print("Nothing to move - already tidy.")
        elif args.dry_run:
            _print_moves(moves, True)
        else:
            _print_moves(moves, False)
            apply_moves(moves, cfg, resolve_target(cfg, source))
        for name, reason in skipped:
            print(f"  - skipped {name}: {reason}")

    print(f"Organizing : {source}")
    run_once()

    if args.watch:
        print(f"\nWatching every {args.watch}s. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(args.watch)
                print(f"\n--- rescan {time.strftime('%H:%M:%S')} ---")
                run_once()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
