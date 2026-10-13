"""Settings, plus where the app keeps its files.

Two things live here:

1. `data_dir()` - the folder the app stores config.json / history.json in.
   During development that's this folder. Once the app is turned into a
   Windows .exe, `__file__` points inside a temporary unpack folder, so we
   switch to %APPDATA%\\DownloadOrganizer instead. That's how real Windows
   apps behave.

2. `load()` / `save()` - read and write config.json, falling back to defaults
   if the file is missing or damaged.
"""

import copy
import json
import os
import sys
from pathlib import Path

DEFAULTS = {
    # None means: use your real Downloads folder / same place as the source.
    "source": None,
    "target": None,

    # Files touched in the last few seconds are probably still downloading.
    "min_age_seconds": 5,

    # Look inside archives while classifying (slower but smarter).
    "smart_detection": True,

    # How many files must share a signal before we suggest a folder for it.
    "min_pattern_files": 3,

    # Put version numbers from a file name into a subfolder, e.g.
    # "Minecraft Mods/1.20.1/". Set to false to keep them flat.
    "version_subfolders": True,

    # After a run, delete any category folders that ended up empty.
    "cleanup_empty_folders": True,

    # Patterns you have accepted. Checked before everything else.
    # Each is {"match": "inner:fabric-mod", "folder": "Minecraft Mods"}.
    "rules": [],

    # Category folder -> list of extensions that belong there.
    "categories": {
        "Images": ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "ico",
                   "tif", "tiff", "heic", "avif"],
        "Videos": ["mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "m4v",
                   "mpg", "mpeg"],
        "Audio": ["mp3", "wav", "flac", "aac", "ogg", "m4a", "opus", "wma",
                  "mid", "midi"],
        "Documents": ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
                      "txt", "md", "csv", "odt", "ods", "rtf"],
        "eBooks": ["epub", "mobi", "azw3", "cbz", "cbr"],
        "Code": ["py", "js", "ts", "java", "c", "cpp", "h", "cs", "go", "rs",
                 "html", "css", "json", "xml", "yaml", "yml", "sql", "php",
                 "rb", "swift", "kt", "lua", "toml", "jar"],
        "Scripts": ["sh", "bat", "ps1", "cmd", "vbs"],
        "Installers": ["exe", "msi", "dmg", "pkg", "deb", "rpm", "appimage",
                       "snap"],
        "Android": ["apk", "aab", "xapk"],
        "Archives": ["zip", "rar", "7z", "tar", "gz", "bz2", "xz", "tgz"],
        "Fonts": ["ttf", "otf", "woff", "woff2", "eot"],
        "3D Models": ["stl", "obj", "3mf", "gltf", "glb", "fbx"],
        "Disk Images": ["iso", "img", "vhd", "vmdk", "vdi"],
        "Torrents": ["torrent"],
    },
}


def data_dir() -> Path:
    """Where config.json and history.json live."""
    if getattr(sys, "frozen", False):        # running as a built .exe
        base = Path(os.environ.get("APPDATA", Path.home())) / "DownloadOrganizer"
    else:                                     # running from source
        base = Path(__file__).parent
    base.mkdir(parents=True, exist_ok=True)
    return base


def config_path() -> Path:
    return data_dir() / "config.json"


def load() -> dict:
    """Read config.json, merged over the defaults."""
    cfg = copy.deepcopy(DEFAULTS)
    path = config_path()
    if path.exists():
        try:
            saved = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                for key, value in saved.items():
                    if key == "categories" and isinstance(value, dict):
                        # Merge so a new default category still shows up.
                        cfg["categories"].update(value)
                    else:
                        cfg[key] = value
        except (OSError, json.JSONDecodeError):
            pass  # damaged file -> defaults are safer than crashing
    return cfg


def save(cfg: dict) -> dict:
    config_path().write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return cfg
