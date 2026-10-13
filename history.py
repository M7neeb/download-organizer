"""The undo history.

Every time the organizer moves files it writes down what it did, as pairs of
"this went from here to there". The undo command reads the most recent run and
puts everything back. That's the whole trick behind an undo button.

We keep a list of runs, newest last, in history.json. Only the last 20 runs are
kept so the file can't grow forever.
"""

import json
import time
from pathlib import Path

import config

MAX_RUNS = 20


def history_path() -> Path:
    return config.data_dir() / "history.json"


def _read() -> list:
    path = history_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _write(runs: list):
    history_path().write_text(json.dumps(runs, indent=2), encoding="utf-8")


def record(moves) -> None:
    """Remember a run. `moves` is a list of (source_path, destination_path)."""
    if not moves:
        return
    runs = _read()
    runs.append({
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "moves": [[str(src), str(dst)] for src, dst in moves],
    })
    _write(runs[-MAX_RUNS:])


def runs() -> list:
    """All remembered runs, newest last."""
    return _read()


def last_run():
    runs_list = _read()
    return runs_list[-1] if runs_list else None


def undo_last() -> tuple:
    """Put back the files moved by the most recent run.

    Returns (restored_count, list_of_problem_messages).
    """
    runs = _read()
    if not runs:
        return 0, ["Nothing to undo."]

    run = runs.pop()
    restored = 0
    problems = []
    moves = run.get("moves", [])

    # The folder each file came from. We never delete these, but we do tidy up
    # the category folders the run created inside them.
    source_roots = {Path(src).parent for src, _dst in moves}

    # Reverse order, so if two things moved in one run we unwind cleanly.
    for src, dst in reversed(moves):
        src_path, dst_path = Path(src), Path(dst)
        try:
            if not dst_path.exists():
                problems.append(f"missing already: {dst_path.name}")
                continue
            src_path.parent.mkdir(parents=True, exist_ok=True)
            if src_path.exists():
                # Something else is sitting there now - don't clobber it.
                stem, suffix = src_path.stem, src_path.suffix
                counter = 1
                while True:
                    candidate = src_path.with_name(f"{stem} (restored {counter}){suffix}")
                    if not candidate.exists():
                        src_path = candidate
                        break
                    counter += 1
            dst_path.replace(src_path)
            restored += 1
            _prune_empty_parents(dst_path.parent, source_roots)
        except OSError as exc:
            problems.append(f"{dst_path.name}: {exc}")

    _write(runs)
    return restored, problems


def _prune_empty_parents(folder: Path, stop_at: set):
    """Remove folders we emptied, working upwards, never past the stop points."""
    while folder not in stop_at:
        try:
            if not folder.is_dir() or any(folder.iterdir()):
                break
            folder.rmdir()
        except OSError:
            break
        folder = folder.parent
