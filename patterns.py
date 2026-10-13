"""The pattern engine.

This is the bit that does NOT hard-code anything about Minecraft. Instead every
file gives off a bunch of "signals" - small facts we can measure about it:

  type:image            it really is a picture (from its bytes)
  ext:psd               the name ends in .psd
  inner:pack.mcmeta     the zip contains a file called pack.mcmeta
  inner:AndroidManifest.xml   the zip contains an Android manifest
  name:screenshot       the name contains the word "screenshot"
  prefix:IMG_           the name starts with IMG_
  version:1.20.1        a version number we found in the name

One signal on its own means nothing. But when a bunch of downloaded files all
share the same unusual signal, that is a pattern - and a pattern is a hint that
those files belong together in their own folder.

`suggest()` counts the signals and proposes folders. The user decides whether to
accept a suggestion; accepted ones become "rules" in config.json and from then
on the organizer files matching downloads there automatically.

Adding a new pattern is data, not code: add a line to FRIENDLY_FOLDERS and it
gets a nice name. Anything not listed gets a name worked out automatically.
"""

import re
import zipfile
from pathlib import Path

# --------------------------------------------------------------------------
# What the raw bytes say the file IS
# --------------------------------------------------------------------------
MAGIC_TYPES = [
    (b"\x89PNG\r\n\x1a\n", "image"),
    (b"\xff\xd8\xff", "image"),          # JPEG
    (b"GIF87a", "image"),
    (b"GIF89a", "image"),
    (b"BM", "image"),
    (b"glTF", "model"),
    (b"\x00\x01\x00\x00", "font"),       # TrueType
    (b"OTTO", "font"),                   # OpenType
    (b"wOFF", "font"),
    (b"wOF2", "font"),
    (b"%PDF", "document"),
    (b"PK\x03\x04", "archive"),          # zip family
    (b"Rar!\x1a\x07", "archive"),
    (b"7z\xbc\xaf\x27\x1c", "archive"),
    (b"\x1f\x8b", "archive"),            # gzip
    (b"MZ", "executable"),
    (b"\x7fELF", "executable"),
    (b"ID3", "audio"),
    (b"\xff\xfb", "audio"),
    (b"fLaC", "audio"),
    (b"OggS", "audio"),
]

# Which type folder to fall back to when the name gives us nothing better.
TYPE_FOLDER = {
    "image": "Images", "video": "Videos", "audio": "Audio",
    "document": "Documents", "executable": "Installers", "font": "Fonts",
    "model": "3D Models", "archive": "Archives",
}

# Words in a file name that tell us something useful. Matched lower-cased.
NAME_KEYWORDS = {
    "screenshot": "name:screenshot",
    "screen shot": "name:screenshot",
    "snip": "name:screenshot",
    "whatsapp": "name:whatsapp",
    "invoice": "name:invoice",
    "receipt": "name:receipt",
    "setup": "name:setup",
    "installer": "name:installer",
    "backup": "name:backup",
    "resume": "name:resume",
    "wallpaper": "name:wallpaper",
}

# Prefixes (things like phone/camera naming conventions).
NAME_PREFIXES = {
    "img_": "prefix:IMG_",
    "vid_": "prefix:VID_",
    "dsc_": "prefix:DSC_",
    "pxl_": "prefix:PXL_",
}

# --------------------------------------------------------------------------
# What's *inside* an archive
# --------------------------------------------------------------------------
# Each entry is (test, signal). `test` gets the set of lower-cased names.
def _inner_signals(names):
    out = set()

    def has(pred):
        return any(pred(n) for n in names)

    if "fabric.mod.json" in names:
        out.add("inner:fabric-mod")
    if has(lambda n: n.endswith("mods.toml")):
        out.add("inner:forge-mod")
    if has(lambda n: n.endswith("quilt.mod.json")):
        out.add("inner:quilt-mod")
    if "pack.mcmeta" in names:
        out.add("inner:mcmmeta")
    if has(lambda n: n.startswith("assets/")):
        out.add("inner:assets")
    if has(lambda n: n.startswith("data/")):
        out.add("inner:data")
    if has(lambda n: n.startswith("shaders/")):
        out.add("inner:shaders")
    if "androidmanifest.xml" in names or has(lambda n: n.endswith("classes.dex")):
        out.add("inner:android-app")
    if has(lambda n: n.startswith("word/")):
        out.add("inner:word-doc")
    if has(lambda n: n.startswith("xl/")):
        out.add("inner:excel-doc")
    if has(lambda n: n.startswith("ppt/")):
        out.add("inner:powerpoint-doc")
    if "mimetype" in names and has(lambda n: n.startswith("oebps/")):
        out.add("inner:epub")
    if "package.json" in names:
        out.add("inner:npm-project")
    if "info.json" in names:
        out.add("inner:factorio-mod")
    if "about/about.xml" in names:
        out.add("inner:rimworld-mod")
    if "meta-inf/manifest.mf" in names:
        out.add("inner:java-package")
    if has(lambda n: n.endswith(".class")):
        out.add("inner:java-classes")
    if "modrinth.index.json" in names:
        out.add("inner:modpack")
    if "manifest.json" in names and has(lambda n: n.startswith("overrides/")):
        out.add("inner:modpack")
    if "index.html" in names or "index.htm" in names:
        out.add("inner:web-page")
    if "dockerfile" in names:
        out.add("inner:docker")

    return out


# Nice folder names for signals we recognise. Anything missing gets a name
# generated from the signal itself, so unknown patterns still work.
FRIENDLY_FOLDERS = {
    "inner:fabric-mod": "Minecraft Mods",
    "inner:forge-mod": "Minecraft Mods",
    "inner:quilt-mod": "Minecraft Mods",
    "inner:mcmmeta": "Minecraft Packs",
    "inner:shaders": "Minecraft Shaders",
    "inner:modpack": "Modpacks",
    "inner:android-app": "Android Apps",
    "inner:word-doc": "Word Documents",
    "inner:excel-doc": "Spreadsheets",
    "inner:powerpoint-doc": "Presentations",
    "inner:epub": "eBooks",
    "inner:npm-project": "Node Projects",
    "inner:java-package": "Java Libraries",
    "inner:java-classes": "Java Libraries",
    "inner:web-page": "Web Pages",
    "inner:docker": "Docker Projects",
    "inner:factorio-mod": "Factorio Mods",
    "inner:rimworld-mod": "RimWorld Mods",
    "name:screenshot": "Screenshots",
    "name:whatsapp": "WhatsApp",
    "name:invoice": "Invoices",
    "name:receipt": "Receipts",
    "name:setup": "Installers",
    "name:installer": "Installers",
    "name:backup": "Backups",
    "name:resume": "Resumes",
    "name:wallpaper": "Wallpapers",
    "prefix:IMG_": "Phone Photos",
    "prefix:VID_": "Phone Videos",
    "prefix:DSC_": "Camera Photos",
    "prefix:PXL_": "Phone Photos",
}


# Signals that are safe to sort into their own folder straight away, without
# asking. Everything else becomes a *suggestion* instead. Keys are signals,
# values are the folder name.
AUTO_SIGNALS = {
    "inner:fabric-mod": "Minecraft Mods",
    "inner:forge-mod": "Minecraft Mods",
    "inner:quilt-mod": "Minecraft Mods",
    "inner:mcmmeta": "Minecraft Packs",
    "inner:shaders": "Minecraft Shaders",
    "inner:modpack": "Modpacks",
    "inner:android-app": "Android",
    "inner:word-doc": "Documents",
    "inner:excel-doc": "Documents",
    "inner:powerpoint-doc": "Documents",
    "inner:epub": "eBooks",
    "name:screenshot": "Screenshots",
    "name:whatsapp": "WhatsApp",
    "prefix:IMG_": "Phone Photos",
    "prefix:VID_": "Phone Videos",
    "prefix:DSC_": "Camera Photos",
    "prefix:PXL_": "Phone Photos",
}

# When several signals match one file, the higher priority wins. "inner" facts
# come from really opening the file, so they beat guesses from the name.
SIGNAL_PRIORITY = {"inner": 4, "name": 3, "prefix": 3, "ext": 2,
                   "type": 1, "version": 0}


# --------------------------------------------------------------------------
# Running one file through the signal detector
# --------------------------------------------------------------------------
def _read_head(path: Path, size: int = 32) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read(size)
    except OSError:
        return b""


def magic_type(head: bytes):
    """Content type straight from the file's first bytes, or None."""
    for signature, name in MAGIC_TYPES:
        if head.startswith(signature):
            return name
    if head[4:8] == b"ftyp":
        return "video"
    if head.startswith(b"\x1a\x45\xdf\xa3"):
        return "video"                    # MKV / WebM
    if head.startswith(b"RIFF"):
        kind = head[8:12]
        if kind == b"WAVE":
            return "audio"
        if kind == b"AVI ":
            return "video"
        if kind == b"WEBP":
            return "image"
    return None


def _looks_like_text(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            raw = f.read(2048)
    except OSError:
        return False
    return b"\x00" not in raw and len(raw) > 0


def analyze(path: Path) -> dict:
    """Work out all the signals for a single file.

    Returns a dict with: type, ext, inner (set), names (set), prefixes (set),
    versions (set).
    """
    name = path.name
    stem = path.stem.lower()
    ext = path.suffix.lstrip(".").lower()

    info = {
        "type": magic_type(_read_head(path)),
        "ext": ext,
        "inner": set(),
        "names": set(),
        "prefixes": set(),
        "versions": set(),
    }

    # If there's no magic signature, a readable-text check helps a lot.
    if info["type"] is None and _looks_like_text(path):
        info["type"] = "text"

    # Version numbers, but with the "1.20.1"-style check first so we don't
    # grab unrelated numbers.
    for match in re.findall(r"\b\d+\.\d+(?:\.\d+)?\b", stem):
        info["versions"].add(f"version:{match}")

    # Name keywords.
    lowered = name.lower()
    for word, signal in NAME_KEYWORDS.items():
        if word in lowered:
            info["names"].add(signal)

    # Name prefixes.
    for prefix, signal in NAME_PREFIXES.items():
        if lowered.startswith(prefix):
            info["prefixes"].add(signal)

    # Inside archives (only zip-family can be read without extra libraries).
    if ext in {"jar", "zip", "apk", "aab", "xapk", "epub", "docx", "xlsx",
               "pptx", "odt", "ods", "mrpack"} or info["type"] == "archive":
        try:
            with zipfile.ZipFile(path) as zf:
                names = {n.lower().lstrip("./") for n in zf.namelist()}
            info["inner"] |= _inner_signals(names)
        except (zipfile.BadZipFile, OSError, ValueError):
            pass  # not a readable zip; that's fine

    return info


def signals(info: dict) -> set:
    """Flatten an info dict into the set of signal strings."""
    out = set()
    if info.get("type"):
        out.add(f"type:{info['type']}")
    if info.get("ext"):
        out.add(f"ext:{info['ext']}")
    for group in ("inner", "names", "prefixes", "versions"):
        out |= set(info.get(group, ()))
    return out


def friendly_folder(signal: str) -> str:
    """Turn a signal into a human folder name."""
    if signal in FRIENDLY_FOLDERS:
        return FRIENDLY_FOLDERS[signal]
    kind, _, rest = signal.partition(":")
    if kind == "version":
        return f"Version {rest}"
    if kind == "prefix":
        rest = rest.strip("_")
    label = rest.replace(".", " ").replace("-", " ").replace("_", " ")
    return label.title()


# --------------------------------------------------------------------------
# Turning signals into folder suggestions
# --------------------------------------------------------------------------
def suggest(files, cfg):
    """Look for patterns across a batch of files.

    `files` is a list of (path, info) pairs. Returns a list of suggestion
    dicts, most common first:

        {"signal": "inner:fabric-mod", "count": 8,
         "folder": "Minecraft Mods", "examples": ["sodium.jar", ...]}
    """
    min_files = int(cfg.get("min_pattern_files", 3))
    ext_lookup = cfg.get("_ext_lookup", {})
    taken = {rule["match"] for rule in cfg.get("rules", [])}

    counts, examples = {}, {}
    for path, info in files:
        for signal in signals(info):
            kind = signal.split(":", 1)[0]

            # type/ext are handled by the normal rules. Versions belong as a
            # subfolder, not a top-level folder of their own.
            if kind in ("type", "version"):
                continue
            # An extension we already route somewhere needs no suggestion.
            if kind == "ext" and signal.split(":", 1)[1] in ext_lookup:
                continue
            # Signals that already sort themselves need no suggestion.
            if signal in AUTO_SIGNALS:
                continue
            # A rule already covers this signal.
            if signal in taken:
                continue

            counts[signal] = counts.get(signal, 0) + 1
            examples.setdefault(signal, [])
            if len(examples[signal]) < 4:
                examples[signal].append(path.name)

    out = []
    for signal, count in counts.items():
        if count < min_files:
            continue
        out.append({
            "signal": signal,
            "count": count,
            "folder": friendly_folder(signal),
            "examples": examples[signal],
        })

    # Strongest patterns first, then alphabetically so the list is stable.
    out.sort(key=lambda s: (-s["count"], s["signal"]))
    return out
