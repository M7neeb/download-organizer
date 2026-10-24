# Build the real Download Organizer — file by file

This is the "type the actual app yourself" guide. At the end you will have the
exact same seven files as the finished project, and you will understand what
every single block of them does.

It is written for someone who has **never written Python before**. Every new
word is explained. Nothing is skipped. Nothing says "just trust me".

## How to use this guide

The app is seven files. We build them **in the right order** — each one only
uses things the ones before it already explained. For every file you get:

- **What it is** and why it exists at all.
- **The code, in chunks.** Type each chunk into your editor as you read it. Do
  not copy-paste; typing is how your hands learn the shape of the language.
- **Why it looks like that** — the reasoning behind the choices.
- **A checkpoint** — a command to run and the output you should see. If it
  matches, move on. If not, we fix it before continuing. This is the single most
  important habit in this whole guide: never build on top of something you have
  not seen working.

> **Two guides, two jobs.** `TUTORIAL.md` teaches the *ideas* by building
> throwaway mini-versions. **This file** builds the real app. If a concept here
> feels too fast, read the matching part of `TUTORIAL.md` first.

## The seven files, and why they are separate

```
config.py          settings, and where files are stored
patterns.py        works out what a file IS (the detective)
history.py         remembers moves so undo is possible
organizer.py       the engine: decide where each file goes, then move it
make_demo_files.py builds a fake Downloads folder for safe testing
gui.py             the desktop window you click
run.py             the 7-line entry point for the .exe
```

Splitting the app up is not decoration. Each file has **one job**, so when
something breaks you know where to look, and when you want a web version later
you add a new "front door" without touching the engine.

---

# Part 1 — Setting up your computer

## 1.1 Install Python

1. Go to <https://www.python.org/downloads/> and download Python for Windows.
2. Run the installer. **On the very first screen, tick "Add python.exe to
   PATH".** This one checkbox is the difference between `python` working and a
   confusing error later. If you miss it, run the installer again and pick
   "Modify".
3. Finish the install.

Test it. Press the Start button, type `PowerShell`, open it, and type:

```powershell
python --version
```

You should see something like:

```
Python 3.13.1
```

> **What happened?** You ran the program `python` with the instruction
> `--version` ("tell me your version"). The word after the program name is
> called an **argument** — extra instructions you hand to a program.

If you instead see `python : The term 'python' is not recognized`, the PATH
checkbox was missed. Reinstall with it ticked.

## 1.2 Make the project folder

Still in PowerShell:

```powershell
cd ~
mkdir download-organizer
cd download-organizer
```

- `cd ~` — "change directory to my home folder". `~` is shorthand for your user
  folder (`C:\Users\Munee`).
- `mkdir download-organizer` — make a new folder.
- `cd download-organizer` — go into it.

Check where you are with `pwd` ("print working directory").

## 1.3 Get a real editor

Install **Visual Studio Code**: <https://code.visualstudio.com/>

Then, from your project folder in PowerShell:

```powershell
code .
```

The `.` means "this folder" — VS Code opens with your project ready. You will
write every file in here. Open the built-in terminal with **Terminal → New
Terminal** so you can run code without switching windows.

## 1.4 One thing to know before you start: indentation

Python does not use `{ }` to group lines. It uses **indentation** — spaces at
the start of a line.

```python
if True:
    print("this is inside the if")     # 4 spaces: part of the if
print("this is outside")               # no spaces: not part of the if
```

**Use exactly four spaces. Never a Tab.** Mixing them causes errors that are
painful to find. VS Code inserts 4 spaces when you press Tab inside a `.py`
file, so it is handled for you — but understand *why* it matters.

---

# Part 2 — `config.py`: settings and storage

This file holds every default setting, plus the two functions that read and
write them. Nothing else in the app needs to know *where* settings are stored —
they all ask this file.

Create a new file called `config.py`.

## 2.1 Chunk 1 — the docstring and imports

Type this first:

```python
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
```

**Why each line**

- The text in `"""triple quotes"""` at the very top is a **docstring** — a
  description of the file. Python stores it as the module's documentation. It
  is for humans, not the computer.
- `import copy` — Python's toolbox for **copying** data properly. We need it so
  that when we hand out the defaults, a caller cannot accidentally change the
  master copy.
- `import json` — read and write the **JSON** format (the text format our
  settings file uses).
- `import os` — lets us look up **environment variables**, like `%APPDATA%`.
- `import sys` — gives us `sys.frozen`, which tells us whether we are running
  as a packaged `.exe`. We will see exactly how in a moment.
- `from pathlib import Path` — loads the `Path` tool from the `pathlib` toolbox.
  `Path` is how we handle file paths so they work on any computer.

> **`import x` versus `from x import y`.** `import json` loads the whole toolbox,
> so you write `json.dumps(...)`. `from pathlib import Path` loads just one tool,
> so you write `Path(...)` with no prefix. Same idea, different style.

## 2.2 Chunk 2 — the defaults

Every setting the app has, with its starting value. Add this below the imports:

```python
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
```

> **Do not run the file yet.** This block leaves the `DEFAULTS` dictionary
> deliberately unclosed — the next chunk adds the `categories` table inside it
> and puts the closing `}` on. Type both chunks, then run the checkpoint at 2.6.

**What is this?** A **dictionary** — a collection of labelled boxes. `"source"`
is the label (the **key**), `None` is what is inside (the **value**). You look a
value up by its key: `DEFAULTS["min_age_seconds"]` gives you `5`.

**Why the values are what they are**

- `None` is Python's word for "nothing". `"source": None` means "no folder
  chosen yet — fall back to the real Downloads folder". Code later checks
  `if cfg.get("source")` which is only true when a real value is set.
- `"min_age_seconds": 5` — a file changed in the last 5 seconds is probably
  still being written by your browser. We leave it alone.
- `"smart_detection": True` — do the "look inside the archive" step. It is
  slower but smarter, so it is on by default.
- `"min_pattern_files": 3` — one file having a trait is a coincidence; three is
  a pattern. That is the number that makes the pattern engine trustworthy.
- `"rules": []` — an empty **list** (note the square brackets). Accepted
  patterns get appended here later.

`True` and `False` are Python's two boolean (yes/no) values. Capital first
letter, always.

## 2.3 Chunk 3 — the categories table

Now the big one. Add this inside the same dictionary, right after `"rules": [],`:

```python
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
```

**Why a dictionary instead of 15 separate lists?** Because the app needs to turn
this into "extension -> folder" lookups, and a dictionary is the natural way to
say "folder -> its extensions". The **closing `}` on its own line** ends both
the `categories` dictionary and the `DEFAULTS` dictionary — count the braces if
it looks confusing.

Notice the long lists are **wrapped onto two lines** with the extras indented.
Python allows a list to carry on across lines as long as there is an open
bracket, so this is purely for readability.

> **This table is the "dumb" part of the app.** It is the name-based fallback.
> The clever content detection comes in `patterns.py`. Having this as a plain
> table is deliberate: you can add a file type without touching any logic.

## 2.4 Chunk 4 — where files are stored

Below the `DEFAULTS` dictionary (make sure you are back at the left margin), add:

```python
def data_dir() -> Path:
    """Where config.json and history.json live."""
    if getattr(sys, "frozen", False):        # running as a built .exe
        base = Path(os.environ.get("APPDATA", Path.home())) / "DownloadOrganizer"
    else:                                     # running from source
        base = Path(__file__).parent
    base.mkdir(parents=True, exist_ok=True)
    return base
```

**Line by line**

- `def data_dir() -> Path:` — defines a **function** named `data_dir`. The
  `() ` means it takes no inputs. The `-> Path` is a **type hint**: it tells
  humans (and editors) that this function hands back a `Path` object. Python
  does not enforce it, but it documents intent.
- `getattr(sys, "frozen", False)` — asks the `sys` object for an attribute
  called `frozen`. If it is not there, return `False`. When PyInstaller builds
  an `.exe`, it sets `sys.frozen = True`. So this line is really asking: **"am I
  running as a packaged app?"**
- `Path(__file__).parent` — `__file__` is the path of *this* script. `.parent`
  is the folder containing it. So when running from source, we store files next
  to the code.
- `Path(os.environ.get("APPDATA", Path.home())) / "DownloadOrganizer"` — read
  the `APPDATA` environment variable (a standard Windows folder for app data).
  If it does not exist, fall back to your home folder. Then `/ "DownloadOrganizer"`
  appends a subfolder. **The `/` operator on `Path` joins path parts** — on
  Windows it produces a backslash, on Linux a forward slash, and you never worry
  about which.
- `base.mkdir(parents=True, exist_ok=True)` — make the folder. `parents=True`
  creates any missing parent folders too; `exist_ok=True` means "do not complain
  if it already exists".
- `return base` — hand the path back to whoever called us.

**Why the `%APPDATA%` branch exists at all:** when the app is packed into a
single `.exe`, the code inside is unpacked to a temporary folder that gets
deleted. Saving settings there would lose them on every run. Real Windows apps
store data in `%APPDATA%`, so we do the same.

## 2.5 Chunk 5 — reading and writing settings

Add these three functions at the bottom of the file:

```python
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
```

**`config_path()`** — trivial, but it means the filename is written down in
exactly one place. If we ever rename it, we change one line.

**`load()` — the important one. Walk through it:**

1. `copy.deepcopy(DEFAULTS)` — a **deep copy** of the defaults. Normally
   `cfg = DEFAULTS` would just give a second name to the *same* dictionary, so
   editing `cfg` would corrupt the defaults. `deepcopy` makes a fully separate
   copy, nested dictionaries included. This is a classic Python trap.
2. `path.exists()` — only try to read if the file is actually there. First run
   has no file, so we simply keep the defaults.
3. `json.loads(...)` — turns the file's text into Python data. `read_text()`
   needs `encoding="utf-8"` so non-English characters survive.
4. The inner loop copies saved values over the defaults:
   - For `categories`, it uses `.update()` to **merge** rather than replace. Why?
     If a future version of the app adds a new default category, a user's saved
     file (which lacks it) should still get it. Merging keeps both.
   - For everything else, the saved value wins.
5. `except (OSError, json.JSONDecodeError): pass` — if the file is unreadable or
   corrupted, do nothing and carry on with the defaults. **Never let a damaged
   settings file stop the app from starting.**

**`save()`** — `json.dumps(cfg, indent=2)` turns the dictionary back into text,
with 2-space indentation so it is human-readable. `write_text` writes it.

## 2.6 Checkpoint

In the VS Code terminal, in your project folder:

```powershell
python -c "import config; print(config.load()['min_age_seconds'])"
```

You should see:

```
5
```

`-c` means "run this little bit of code". It imports your file and prints one
value from it, which proves the file has no syntax errors and the defaults work.

Then try saving and re-reading:

```powershell
python -c "import config; c=config.load(); c['min_age_seconds']=9; config.save(c); print(config.load()['min_age_seconds'])"
```

You should see `9`, and a new `config.json` file appears in your folder. Open it
in VS Code to see what the app just wrote. Change it back later with:

```powershell
python -c "import config; c=config.load(); c['min_age_seconds']=5; config.save(c)"
```

> **Checkpoint rule.** Do not move on until the number prints. A single missing
> quote mark in a dictionary this long is easy to miss, and this is how you
> catch it while the mistake is still tiny.

---

# Part 3 — `patterns.py`: working out what a file really is

This is the detective. It does **not** hard-code Minecraft or anything else.
Instead it measures small facts about each file, called **signals**, and the
rest of the app decides what to do with them:

```
type:image              the bytes say it is a picture
ext:psd                 the name ends in .psd
inner:pack.mcmeta       the zip contains a file called pack.mcmeta
name:screenshot         the name contains the word "screenshot"
prefix:IMG_             the name starts with IMG_
version:1.20.1          a version number appears in the name
```

One signal alone is meaningless. Several files sharing an unusual signal is a
**pattern** — and that is what the app suggests folders from.

Create `patterns.py`.

## 3.1 Chunk 1 — docstring and imports

```python
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
```

- `import re` — **regular expressions**, a mini-language for finding patterns in
  text. We use it to spot version numbers in file names.
- `import zipfile` — read inside `.zip` archives. This is the superpower: a mod,
  a resource pack and a random zip are all the same format, and only the
  *contents* tell them apart.
- `from pathlib import Path` — file paths again.

## 3.2 Chunk 2 — the bytes table

```python
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
```

**What this is:** a list of `(signature, type)` pairs. Each **signature** is the
literal start of a file of that type. Note the `b` before the quotes: that means
**bytes**, not text.

- `b"\x89PNG\r\n\x1a\n"` — the 8 bytes every PNG starts with. `\x89` is a byte
  written in hexadecimal, because it is not a typable character. `\r\n` is the
  carriage-return + newline pair, part of the PNG signature.
- `(b"BM", "image")` — a two-character signature. It is short, so in theory it
  could match a text file starting with the letters "BM"; real-world files are
  rarely that unlucky, and this is a sorter, not a forensic tool.
- We use a **list of tuples** (a tuple is like a list but fixed) instead of a
  dictionary because we check them *in order* and different signatures map to
  the same type.

> **Why bytes and not the file name?** Because names lie. We will prove that in
> a minute.

## 3.3 Chunk 3 — the type-to-folder fallback

```python
# Which type folder to fall back to when the name gives us nothing better.
TYPE_FOLDER = {
    "image": "Images", "video": "Videos", "audio": "Audio",
    "document": "Documents", "executable": "Installers", "font": "Fonts",
    "model": "3D Models", "archive": "Archives",
}
```

This is the plain lookup: the detective says "this is an image", the engine asks
this table "so where do images go?". Note `"text"` is missing on purpose — text
files have no obvious single home, so they fall through to the extension and the
`Other` folder unless a signal says otherwise.

## 3.4 Chunk 4 — name-based clues

```python
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
```

**Keywords** are things found *anywhere* in the name (`my screenshot 3.png`).
**Prefixes** must be at the *start* (`IMG_20240115.jpg`). Different checks, so
two tables.

The values are **signal strings** — the `name:` and `prefix:` prefixes are a
label saying where the signal came from. That label becomes important later when
the app decides which signal is more trustworthy.

`snip` is in there because Windows' Snipping Tool saves files like
`Snip_2024.png`. `dsc_` is a Nikon-style camera prefix; `pxl_` is a Google Pixel
photo. All lower-cased, because we compare against a lower-cased name.

## 3.5 Chunk 5 — looking inside an archive

This is the heart of the "look inside the file" idea.

```python
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
```

**The signature:** it takes `names` — the set of file names *inside* an archive,
all lower-cased — and returns a set of signals.

The leading `_` in `_inner_signals` is a convention meaning "internal helper,
not for outside use". Python does not enforce it; it is a hint to readers.

**Three ideas to understand:**

1. **`set()`, `.add()`, `in`** — a **set** is an unordered bag of unique items.
   We use it because we only care whether something is present, never how many
   times. `"info.json" in names` is a membership test.
2. **The inner `has(pred)` helper** — `pred` is short for "predicate", a function
   that returns True or False. `has` returns True if **any** name inside the
   archive satisfies it. This saves writing `any(... for n in names)` twenty
   times.
3. **`lambda n: n.endswith("mods.toml")`** — a **lambda** is a tiny throwaway
   function with no name. It means "given an `n`, tell me if it ends with
   `mods.toml`". You need this because `has` wants a function to test with, and
   writing a full `def` for each of twenty checks would be absurd.

**Why these particular names?** They are real markers, not guesses:

- `fabric.mod.json` only exists in a **Fabric** mod.
- `mods.toml` ends a **Forge** mod's metadata.
- `pack.mcmeta` is in every Minecraft **pack** (resource or data).
- `AndroidManifest.xml` / `classes.dex` are inside every **Android** app.
- `word/`, `xl/`, `ppt/` are the internal folders of Word, Excel and PowerPoint
  files (they are zip files underneath!).
- `mimetype` + `OEBPS/` is how an **EPUB** book is laid out.
- `info.json` is a **Factorio** mod; `about/about.xml` is **RimWorld**.
- `modrinth.index.json` or `manifest.json` + `overrides/` marks a **modpack**.
- `meta-inf/manifest.mf` plus `.class` files means a **Java** package.

> **This is the "recognise patterns" part you asked for.** Not one line says
> "put Minecraft files in a Minecraft folder". It says "if a zip contains
> `pack.mcmeta`, emit `inner:mcmmeta`". A *different* table decides what folder
> `inner:mcmmeta` means, and the user can override that. Adding a new game is
> one line here.

## 3.6 Chunk 6 — nice folder names

```python
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
```

**This table is the whole "learn new patterns" mechanism.** A signal like
`inner:factorio-mod` is computer-speak; a human wants "Factorio Mods". Notice
several signals can map to the same folder (`fabric-mod`, `forge-mod` and
`quilt-mod` all become "Minecraft Mods") — that is fine, and it is why this is a
dictionary mapping *signal -> folder*, not the other way round.

Any signal **not** in this table still works; it just gets an automatically
generated name from `friendly_folder()` further down.

## 3.7 Chunk 7 — which patterns sort themselves

```python
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
```

**The difference between `FRIENDLY_FOLDERS` and `AUTO_SIGNALS` is the whole
philosophy of the app:**

- **`AUTO_SIGNALS`** — patterns so obvious and safe that the app sorts them
  automatically. A screenshot going to `Screenshots/` needs no permission.
- **Everything else** — the app *suggests* a folder and waits for the user. That
  is why Factorio and RimWorld mods appear in `FRIENDLY_FOLDERS` (they get a nice
  name when suggested) but **not** in `AUTO_SIGNALS` (the app does not presume).

So a Minecraft mod self-sorts; Factorio mods produce a suggestion you approve
once. That is a deliberate design choice about trust, and it is data, not code —
adding a new auto-rule is one line here.

## 3.8 Chunk 8 — the trust ranking

```python
# When several signals match one file, the higher priority wins. "inner" facts
# come from really opening the file, so they beat guesses from the name.
SIGNAL_PRIORITY = {"inner": 4, "name": 3, "prefix": 3, "ext": 2,
                   "type": 1, "version": 0}
```

A file can carry many signals at once. If one says `inner:epub` and another says
`ext:zip`, which wins? This table answers that by ranking the **kind** of signal
(the part before the colon):

| kind | rank | why |
|---|---|---|
| `inner` | 4 | we actually opened the file — most trustworthy |
| `name` | 3 | a strong hint from the filename |
| `prefix` | 3 | likewise |
| `ext` | 2 | just the ending, easily wrong |
| `type` | 1 | real, but generic ("it's a zip") |
| `version` | 0 | never used to pick a folder, only a subfolder |

Being explicit about trust is what stops a `.zip` extension from overruling the
fact that the archive plainly contains a Minecraft pack.

## 3.9 Chunk 9 — reading the bytes

Now the functions. First, two small ones:

```python
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
```

**`_read_head`**: `open(path, "rb")` opens the file for reading in **binary**
mode (`r` = read, `b` = binary). `with ... as f:` closes the file automatically
when the block ends. `size: int = 32` is a **default argument** — call
`_read_head(p)` and you get 32 bytes; call `_read_head(p, 8)` for 8. If anything
goes wrong (a locked file, a permission problem) we return empty bytes `b""`
rather than crashing. A sorter should never fall over because one file was busy.

**`magic_type`**: loops through the table and returns the first type whose
signature matches the start of the bytes.

Then three checks that the table cannot do:

- `head[4:8] == b"ftyp"` — the MP4 family puts its marker **not at the start**
  but at bytes 4–7. `head[4:8]` is a **slice**: characters 5 to 8, because
  Python counts from 0. So this asks "are bytes 5–8 the letters `ftyp`?".
- MKV and WebM start with a four-byte marker we cannot write as neat text, so we
  compare the escaped bytes instead.
- `RIFF` is a **container**: the same four letters begin WAV audio, AVI video and
  WEBP images. We peek further in (`head[8:12]`) to tell them apart.

`return None` means "I have no idea", letting the caller try something else.

## 3.10 Chunk 10 — is it text at all?

```python
def _looks_like_text(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            raw = f.read(2048)
    except OSError:
        return False
    return b"\x00" not in raw and len(raw) > 0
```

Text files never contain a **null byte** (`\x00`); binary files are full of
them. So this one test separates "readable text" from "a picture or a movie"
without guessing from the name. The `len(raw) > 0` part rejects empty files.

This check matters: without it, we might try to "read" a video as text later.

## 3.11 Chunk 11 — analysing one file

```python
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
```

- `path.name` — the file name with extension (`holiday.jpg`).
- `path.stem` — the name **without** the extension (`holiday`).
- `path.suffix` — the extension **with** the dot (`.jpg`). `.lstrip(".")` removes
  the dot; `.lower()` normalises `JPG` to `jpg`.
- The `info` dictionary groups results by kind: `inner` (from inside the zip),
  `names`, `prefixes`, `versions`. Starting them as empty sets means we can
  `.add()` to them without checking whether they exist.

Continue the same function:

```python
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
```

**The regular expression** `r"\b\d+\.\d+(?:\.\d+)?\b"` deserves a slow read — it
finds version numbers like `1.20` or `1.20.1`:

- The `r` before the quote means a **raw string**: backslashes are taken
  literally, which is what you want for regexes.
- `\b` — a **word boundary** (the edge of a word), so we do not match the middle
  of a longer string.
- `\d+` — one or more **digits**.
- `\.` — a literal dot (escaped, because an unescaped `.` means "any character").
- `(?:\.\d+)?` — an optional group: a dot plus more digits, present zero or one
  time. The `?:` means "do not capture this group separately".
- So it matches `1.20` and `1.20.1`, and not `1234`.

`re.findall` returns every match in the name. Each becomes a `version:...`
signal.

> **Why we do not take just any number.** A filename like `setup-2024.exe`
> contains a number, but it is a year, not a version. Requiring at least one dot
> (`\d+\.\d+`) keeps us from grabbing junk.

Then the keyword loop and the prefix loop. `lowered.startswith(prefix)` checks
the beginning of the name, which is why prefixes are a separate table.

Finish the function:

```python
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
```

- The `in { ... }` test checks whether the extension is in that set. We only try
  to open **zip-family** files, because that is what Python can read for free.
- `zipfile.ZipFile(path)` opens the archive; `zf.namelist()` lists the paths
  inside it.
- `{n.lower().lstrip("./") for n in zf.namelist()}` is a **set comprehension** —
  a compact way to build a set. It lower-cases each name and strips leading
  `./` so comparisons are reliable. (Some archives store paths as
  `./META-INF/...`.)
- `info["inner"] |= _inner_signals(names)` — `|=` merges one set into another:
  "add everything from the right-hand set to this one".
- The `except` catches a corrupt or password-protected archive and simply moves
  on. **A sorter must never crash on one bad file.**

## 3.12 Checkpoint — the magic trick

Before writing more, prove the core idea works. Run:

```powershell
python -c "import patterns; from pathlib import Path; p=Path('patterns.py'); i=patterns.analyze(p); print(sorted(patterns.signals(i)))"
```

You should see something like:

```
['ext:py', 'type:text']
```

Now the fun test: copy any PNG into your folder and rename it to `trick.txt`,
then run:

```powershell
python -c "import patterns; from pathlib import Path; i=patterns.analyze(Path('trick.txt')); print('type is:', i['type'])"
```

It prints `type is: image` — **even though the file is named `.txt`**. That is
content detection working. Delete `trick.txt` afterwards.

> **If it printed `None`:** the copy may have been truncated. Try a different
> image file.

## 3.13 Chunk 12 — flattening signals

```python
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
```

`analyze` returns a dictionary grouped by kind; this flattens it into one flat
set of strings like `{"type:image", "ext:png", "name:screenshot"}`, which is what
the rest of the app wants to work with.

- `info.get("type")` returns `None` if the key is missing, and `if None:` is
  false — so we only add the signal when there is a type.
- `f"type:{info['type']}"` is an **f-string**: text with `{}` holes filled in.
- The loop merges the four set-groups with `|=`. `set(info.get(group, ()))` wraps
  an empty tuple `()` as a fallback, so a missing group contributes nothing.

## 3.14 Chunk 13 — naming a signal

```python
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
```

This turns any signal into something readable:

- If it is in the table, use the nice name.
- Otherwise split at the colon. `signal.partition(":")` returns three parts:
  everything before, the `:` itself, and everything after. We keep the first and
  last, naming the middle `_` to say "ignored" (a common convention).
- Versions get "Version 1.20.1". Prefixes lose their underscores.
- Otherwise every `.`, `-` and `_` becomes a space, and `.title()` capitalises
  each word. So `inner:factorio-mod` would become "Factorio Mod" if it were not
  already in the table — which is exactly why unknown patterns still work.

## 3.15 Chunk 14 — spotting patterns across many files

```python
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
```

**Counting is the entire pattern engine**, and it is simpler than it looks:

- `min_files` — how many files must share a signal before it is a pattern.
- `taken` — a set of signals the user has **already accepted as rules**, so we do
  not keep suggesting them.
- `counts` — a dictionary counting how many files carry each signal.
- `examples` — up to four file names per signal, so the user can see what we mean.

**Every `continue` is a filter.** We skip signals that are useless for
suggestions:

- `type:` and `version:` — type is too generic, version belongs in a *subfolder*.
- `ext:` that is already routed by the categories table — no need to suggest what
  already works.
- signals in `AUTO_SIGNALS` — they sort themselves already.
- signals already accepted as rules.

`counts.get(signal, 0) + 1` means "whatever the count is so far (or 0), add one"
— the standard way to count things in Python.

Finish the function:

```python
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
```

The sort needs a moment. `key=lambda s: (-s["count"], s["signal"])` sorts by two
things at once:

- `-s["count"]` — the **negative** count, so the biggest count comes first
  (sorting is smallest-first, and a bigger count gives a smaller negative
  number).
- `s["signal"]` — alphabetical, used to break ties, so the list order is stable
  and does not jump around between runs.

That is a genuinely useful Python trick, and worth remembering.

## 3.16 Checkpoint

The demo folder does not exist yet, so for now just confirm the file is valid:

```powershell
python -c "import patterns; print('MAGIC_TYPES:', len(patterns.MAGIC_TYPES), 'FRIENDLY:', len(patterns.FRIENDLY_FOLDERS), 'AUTO:', len(patterns.AUTO_SIGNALS))"
```

Expected:

```
MAGIC_TYPES: 21 FRIENDLY: 31 AUTO: 17
```

You have now written the two "data + brains" files. On to Part 4, where we make
the app actually move files.

---

# Part 4 — `history.py`: remembering what we did

An undo button sounds like magic. It is not. It is just a **written record of
what moved**, kept in a file, read backwards to put things back.

Create `history.py`.

## 4.1 Chunk 1 — docstring and imports

```python
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
```

- `import config` — our own file from Part 2. **This is how the files talk to
each other**: `history` asks `config` where to store its file, instead of
deciding for itself. That is why `config.py` exists.
- `MAX_RUNS = 20` — a **constant** (a named value we do not change). Writing it
at the top and in capitals is a convention meaning "this is a setting for
developers".

## 4.2 Chunk 2 — reading and writing the history file

```python
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
```

**Same pattern as `config.py`:** a function that knows where the file is
(`history_path`), one that reads, one that writes.

- `_read` returns an empty list if the file is missing **or** damaged **or**
  contains something that is not a list. Notice `data if isinstance(data, list)
  else []` — a compact way to say "only trust it if it is the right shape".
  `isinstance(x, list)` asks "is x a list?".
- `_write` saves the list as pretty-printed JSON. Nothing fancy.

Both are marked with a leading `_` because they are internal helpers — the rest
of the app should use the named functions below.

## 4.3 Chunk 3 — recording a run

```python
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
```

- `if not moves: return` — if nothing moved, there is nothing to record. `not []`
  is `True`, so an empty list bails out early.
- `runs.append({...})` — add one **run** to the list. A run is a dictionary with
  a timestamp and the list of moves.
- `time.strftime("%Y-%m-%d %H:%M:%S")` turns the current time into a readable
  string like `2026-09-19 22:30:01`.
- `[[str(src), str(dst)] for src, dst in moves]` converts our list of path pairs
  into lists of **strings**, because JSON cannot store `Path` objects.
- `runs[-MAX_RUNS:]` — a **slice** meaning "the last 20 items". `-20` counts
  from the end, and leaving the right side empty means "to the end". So the file
  never grows past 20 runs.

## 4.4 Chunk 4 — two convenient readers

```python
def runs() -> list:
    """All remembered runs, newest last."""
    return _read()


def last_run():
    runs_list = _read()
    return runs_list[-1] if runs_list else None
```

`last_run` uses a conditional expression: `A if condition else B`. If the list
has something, return the last item (`[-1]`); otherwise return `None`. These two
are small conveniences — the window and the command line could use them, though
in this app the undo path below is the one that really matters.

## 4.5 Chunk 5 — undo

```python
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
```

- `runs.pop()` removes **and returns** the last item. Perfect for undo: take the
  most recent run off the stack.
- We return **two things** wrapped in a tuple: how many files came back, and any
  problems. `-> tuple` documents that.
- `{Path(src).parent for src, _dst in moves}` is a set comprehension collecting
  the folders files came from. These are our **stop points** — we must never
  delete these, which is the safety net for the next function.

Now the loop:

```python
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
```

**Line by line, because this is the trickiest function in the app:**

- `reversed(moves)` — walk the moves from last to first. Undoing in reverse order
  is the safe way to unwind a sequence of changes.
- `if not dst_path.exists(): continue` — if the file is not where we put it, note
  it and skip. Never crash just because the world changed underneath us.
- `src_path.parent.mkdir(parents=True, exist_ok=True)` — make sure the original
  folder still exists (the user might have deleted it) before moving back.
- The `if src_path.exists():` block — the name is taken! Maybe you downloaded a
  new file with the same name since. So we find a free name, exactly like
  `unique_destination` does in the engine, and call it `file (restored 1).ext`.
  **Never overwrite on undo** either.
- `dst_path.replace(src_path)` — the actual move. `Path.replace(target)` moves the
  file, overwriting the target if it exists. Here it is exactly what we mean:
  "put this back where it came from".
- `restored += 1` — `+=` means "add one to itself".
- `except OSError as exc:` — capture the error message and store it as text. The
  underscore-and-name style, `problems.append(f"{dst_path.name}: {exc}")`, gives a
  readable note like `photo.jpg: access denied`.
- `_write(runs)` — save the history **without** the run we just consumed, so a
  second click of Undo undoes the run before it. That is why we keep a list.

## 4.6 Chunk 6 — tidying up emptied folders

```python
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
```

After undo, `Images/` is probably empty and pointless. This removes it — then
keeps climbing to remove an empty `Minecraft/`, and so on.

- `while folder not in stop_at:` — keep climbing until we reach a folder files
  actually came from. **This is the guard that stops us ever deleting your
  Downloads folder.**
- `any(folder.iterdir())` is `True` if the folder has even one thing left in it,
  so we `break` rather than delete something with files in it.
- `folder.rmdir()` removes an **empty** folder. It refuses to remove one with
  contents — a second, built-in safety net.
- `folder = folder.parent` climbs one level up and loops.

> **Two independent safety nets.** Our `stop_at` set, and `rmdir` refusing
> non-empty folders. Either one alone would be enough; both together mean a bug
> in one cannot orphan your files.

## 4.7 Checkpoint

```powershell
python -c "import history; print('nothing to undo:', history.undo_last())"
```

Expected:

```
nothing to undo: (0, ['Nothing to undo.'])
```

That proves the file loads and handles the empty case. We will test a real undo
in Part 6.

---

# Part 5 — `organizer.py`: the engine

This is the biggest, most important file. It ties the other two together and
does the actual work. We build it top to bottom.

Create `organizer.py`.

## 5.1 Chunk 1 — docstring and imports

```python
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
```

- `#!/usr/bin/env python3` on the first line is a **shebang**. On Windows it does
  nothing; on Mac and Linux it lets the file be run directly. Including it is
  harmless and conventional.
- `import argparse` — the toolbox for reading **command-line arguments**
  (`--dry-run`, `--watch 30`).
- `import shutil` — shell utilities; here we use `shutil.move` to move files.
- `import sys` — system-level things; we use it to exit with an error code.
- `import time` — clocks. We use it for file ages and for pausing in watch mode.
- Our own three files, so we can call them by name.

## 5.2 Chunk 2 — constants

```python
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
```

- **`JUNK_NAMES`** — files Windows and macOS sprinkle everywhere, plus our own
  settings files. A set (curly braces, no values) is the right shape for "is
  this name in the list?".
- **`PARTIAL_SUFFIXES`** — while a browser downloads, it names the file
  `movie.mp4.crdownload` (Chrome/Edge) or `.part` (Firefox). Moving those breaks
  the download, so we skip them.
- **`ZIP_KIND`** — the correction table. `patterns` sees `PK\x03\x04` (a zip) in
  everything from a `.docx` to an `.apk`, because they all *are* zips underneath.
  This table says what each such extension really is when it reaches the
  "it's an archive" stage. `.jar` goes to `Code` because Java archives are code
  packages, not user archives.

## 5.3 Chunk 3 — building the extension lookup

```python
def build_extension_lookup(categories: dict) -> dict:
    """{"Images": ["jpg", ...]} -> {"jpg": "Images", ...}."""
    lookup = {}
    for folder, extensions in categories.items():
        for ext in extensions:
            lookup[str(ext).lower().lstrip(".")] = folder
    return lookup
```

Our settings store the table one way (`folder -> list of extensions`) because
that is how a human edits it. But the engine constantly needs the opposite
question answered — "given `jpg`, which folder?" — so we **flip it** into
`extension -> folder` at the start of a run.

- `.items()` gives you both the key and value in one loop.
- `str(ext).lower().lstrip(".")` normalises each extension: string, lower-case,
  no leading dot. That way `JPG`, `.jpg` and `jpg` all become `jpg`.

> **Doing this once, up front, is a real performance idea.** Without it, every
> file would have to search every category's list. With it, every lookup is a
> single dictionary hit.

## 5.4 Chunk 4 — should we touch this file?

```python
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
```

This is the **safety gate**, and it returns **two values**: whether to proceed,
and why not. Returning a reason is what lets the app print a helpful
"skipped bigfile.zip.part: still downloading" instead of silently doing nothing.

- `entry.stat().st_mtime` — the file's **last-modified time**, as a number of
  seconds. `time.time()` is now. Subtracting gives the **age in seconds**.
- `if age < min_age:` — too fresh; the browser is probably still writing it.
- `f"changed {age:.0f}s ago"` — `:.0f` formats the number with **zero decimal
  places**, so `3.9142` prints as `4`.
- If `stat()` fails (a file that vanished between listing and checking) we
  return `True, ""` — allow it — because the read step will handle a missing
  file gracefully anyway.

## 5.5 Chunk 5 — never overwrite

```python
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
```

If `Images/holiday.jpg` already exists and a *different* `holiday.jpg` arrives,
we must not destroy the first. So we try `holiday (1).jpg`, `holiday (2).jpg`,
until we find a free name.

- `dest.stem` is `holiday`, `dest.suffix` is `.jpg`, so the candidate is built by
  re-joining them with a number in between.
- `while True:` with a `return` inside is the standard "search until found"
  pattern. The `return` is what ends the loop — it would spin forever without it.

> **Why not just let it overwrite?** Because the app's job is to *tidy* your
> files. Silently deleting one would be unforgivable. This is the difference
> between a demo and something you would trust with real downloads.

## 5.6 Chunk 6 — reading the whole folder

```python
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
```

This is where the two earlier files meet. For each item in the folder:

- `sorted(source.iterdir())` — list the folder's contents in a stable order, so
  runs are repeatable and the output does not jump around.
- `if not entry.is_file(): continue` — skip subfolders, only handle files.
- Then the safety gate. Note we deliberately do **not** report `system file` as a
  skip — nobody wants a line about `Thumbs.db` every single run.
- `patterns.analyze(entry)` — the detective from Part 3 does its work.
- `files.append((entry, info))` — keep the path **and** its signals together, in
  a tuple.

The result is everything the rest of the app needs, computed once.

## 5.7 Chunk 7 — picking the winning signal

```python
def _best_match(file_signals, mapping):
    """Pick the highest-priority signal present in `mapping`."""
    best, best_rank = None, -1
    for signal in file_signals:
        if signal in mapping:
            rank = patterns.SIGNAL_PRIORITY.get(signal.split(":", 1)[0], 0)
            if rank > best_rank:
                best, best_rank = signal, rank
    return best
```

A file can carry several signals; this finds the most trustworthy one that also
appears in a given table (the user's rules, or the automatic table).

- `best, best_rank = None, -1` — a neat Python trick: **assign two variables at
  once**. We start the best rank at `-1` so any real rank (0 or more) beats it.
- `signal.split(":", 1)[0]` — grab the part before the colon (`inner`, `name`,
  …) to look up its priority. `split(":", 1)` splits on the **first** colon only.
- `.get(..., 0)` — an unknown kind of signal ranks 0, harmlessly low.
- `if rank > best_rank` — strictly greater, so the **first** signal wins any tie.
  Since we iterate a set, ties are rare and harmless.

This is the function that makes "we actually opened the file" beat "the name had
a hint in it".

## 5.8 Chunk 8 — the version subfolder

```python
def _pick_version(file_signals):
    """The version number to use as a subfolder, if there is one."""
    versions = sorted(s.split(":", 1)[1] for s in file_signals
                      if s.startswith("version:"))
    return versions[-1] if versions else None
```

Collect every `version:` signal as a plain string (`1.20`, `1.20.1`), sort them,
and take the **last** one.

**Why the last, not the first?** Because Minecraft mod filenames look like
`jei-15.2.1-1.20.1.jar`: the mod's own version comes first and the *game* version
comes last. Sorted as text, `1.20` sorts before `1.20.1`, and both sort after
`15.2` would... but the point is that taking the last match of a `1.x` pattern is
far more reliable than the first. This one line is the difference between
`Minecraft Mods/1.20.1/` and `Minecraft Mods/15.2/`.

## 5.9 Chunk 9 — the decision itself

```python
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
```

This is the priority ladder from the top of the file, in code:

1. Turn the user's rules into a lookup dictionary (signal -> folder).
2. Ask `_best_match` which rule matches, if any.
3. If a rule matched, use its folder.
4. Otherwise try the automatic patterns.

The `if matched else None` guards against `_best_match` returning `None` (nothing
matched) — you cannot look up `None` in a dictionary.

Continue:

```python
    # Add a version subfolder for archive-style packages (mods, modpacks...).
    if folder and cfg.get("version_subfolders", True) and matched \
            and matched.startswith("inner:"):
        version = _pick_version(sigs)
        if version:
            folder = f"{folder}/{version}"
    if folder:
        return folder
```

So `Minecraft Mods` becomes `Minecraft Mods/1.20.1` **only when** the winning
signal was an `inner:` one (a package we understood). A screenshot matching by
name never gets a version subfolder.

> **The backslash `\` at the end of that `if` line** joins it to the next line,
> because the whole condition would otherwise be too long to read. It is a
> formatting choice — Python ignores the line break as if it were not there.

Finish the function:

```python
    # 3. The file's real type.
    file_type = info.get("type")
    if file_type == "archive":
        return ZIP_KIND.get(info.get("ext"), "Archives")
    if file_type in patterns.TYPE_FOLDER:
        return patterns.TYPE_FOLDER[file_type]

    # 4. Plain extension.
    return ext_lookup.get(info.get("ext"), "Other")
```

- **Step 3** — what the *bytes* said. If it is a zip, `ZIP_KIND` refines it
  (a `.docx` is a Document, not an Archive). Otherwise `TYPE_FOLDER`
  (image -> Images, etc.).
- **Step 4** — the plain extension lookup, which is where the `ext_lookup`
  dictionary from chunk 3 finally gets used.
- `"Other"` is the final fallback. **There is always a home for a file.**

## 5.10 Chunk 10 — planning without moving

```python
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
```

**This separation is the best idea in the whole app.** `plan()` decides
*everything* but moves *nothing*. It returns the full list of intended moves.

That single design decision gives us, for free:

- `--dry-run` (just print the plan instead of applying it),
- the Scan button in the window,
- a preview of any kind you ever want to add.

`resolve_target` is used before it is defined below — that is fine in Python,
because functions are only looked up when they are *called*, not when the file is
read.

## 5.11 Chunk 11 — doing it

```python
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
```

- `dst.parent.mkdir(parents=True, exist_ok=True)` — make sure `Images/` (and any
  parent like `Minecraft Mods/1.20.1/`) exists before moving into it.
- `shutil.move(str(src), str(dst))` — the actual move. It takes strings, hence
  `str(...)`.
- If one file fails, we print a warning and **keep going**. One locked file
  should not abandon the other ninety.
- `_folder` — the folder name is part of each move tuple, but this function does
  not need it. The leading underscore says "intentionally unused".
- `history.record(done)` — and *now* the move is undoable. Notice we record only
  the moves that actually succeeded.

## 5.12 Chunk 12 — tidying up

```python
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
```

After a run, a category might be empty (say, the last image moved out). We remove
it so your folder does not fill up with empty shells. `reverse=True` sorts
backwards, which conveniently puts deeper names first. Same `any(...iterdir())`
check as before: only genuinely empty folders are removed, and only one level
deep (unlike `_prune_empty_parents`, which climbs).

## 5.13 Chunk 13 — where things go

```python
def resolve_source(cfg: dict) -> Path:
    if cfg.get("source"):
        return Path(cfg["source"]).expanduser()
    return Path.home() / "Downloads"


def resolve_target(cfg: dict, source: Path) -> Path:
    if cfg.get("target"):
        return Path(cfg["target"]).expanduser()
    return Path(source)
```

Two tiny but important functions: they turn **settings** into **real paths**.

- If the user chose a folder, use it. Otherwise default to `Downloads`.
- For the target (where category folders are created), default to the **source**
  folder, which is the normal "sort Downloads in place" behaviour.
- `.expanduser()` turns a `~` into your real home folder, so typing `~/Desktop`
  works.

Both the command line and the window call these, so the default logic lives in
exactly one place.

## 5.14 Chunk 14 — printing the plan nicely

```python
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
```

Groups the moves by destination folder so the output reads like a tidy tree
instead of a flat list.

- `groups.setdefault(folder, []).append(...)` — a very handy idiom. It means "get
  the list for this folder; if it does not exist yet, create an empty one first;
  then append". One line instead of three.
- `verb = "would move" if dry_run else "moved"` — the message tells the truth
  about what just happened. **A dry run must never sound like a real run.**
- `\n` at the start of the print adds a blank line for readability.

## 5.15 Chunk 15 — the command line

```python
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
```

`argparse` turns a messy pile of `sys.argv` strings into named values you can
read as `args.watch`, `args.dry_run` and so on.

- `parser.add_argument("source", nargs="?")` — a **positional** argument (you
  give it without a name). `nargs="?"` makes it optional.
- `"--target"` — an **optional** argument, given as `--target C:/somewhere`.
- `action="store_true"` — a plain on/off switch. `--dry-run` becomes `True`;
  without it, `False`.
- `type=int` — convert the text after `--watch` into a number.
- `metavar="SECONDS"` — just how it appears in the help text.

Continue `main`:

```python
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
```

- Load settings, and write `config.json` on the very first run so the file exists
  for the user to inspect and edit.
- Command-line arguments **override** saved settings.
- `--undo` gets handled first and returns early — undo should work even if the
  source folder no longer exists.

Continue:

```python
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
```

- `sys.exit(1)` — quit with a **non-zero** code. That is the convention for "it
  failed", which lets scripts and the shell know it did not work.
- `pats.suggest(...)` returns the suggestions; we print a little table.
  `{...:>3}` right-aligns the number in 3 spaces; `{...:<28}` left-aligns the
  signal in 28. **Column formatting with f-strings** is worth learning.
- `cfg.setdefault("rules", [])` — get `rules`, creating an empty list if missing.
  Then append the new rule. This is how `--accept` saves a pattern.
- `args.folder or patterns.friendly_folder(...)` — use the folder the user gave,
  otherwise generate a name. `or` returns the right side when the left is empty
  (`None`), a neat shorthand.
- We stash the extension lookup inside `cfg` as `_ext_lookup` so `suggest()` can
  see it. It is a small in-memory convenience, never saved to disk.

Finish `main`:

```python
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
```

- `run_once` is defined **inside** `main` because it closes over `source`, `cfg`
  and `args` — a **nested function**. It is invisible outside `main`, which is
  exactly right; nothing else should call it.
- `time.sleep(args.watch)` pauses the program for that many seconds. **Watch
  mode is really just this loop.** Keep the number sensible; a tiny value would
  hammer your disk.
- `except KeyboardInterrupt` catches **Ctrl+C** and exits politely, instead of
  dumping a scary traceback.

## 5.16 Chunk 16 — the entry line

```python
if __name__ == "__main__":
    main()
```

**This line is worth understanding properly.** Every file has a built-in variable
`__name__`. When a file is **run directly** (`python organizer.py`), `__name__`
is `"__main__"`. When a file is **imported** by another file, `__name__` is the
file's name instead.

So this says: "only run the command-line interface when I am started directly."
That is why `gui.py` can `import organizer` without accidentally launching the
CLI — importing it leaves `__name__` as `"organizer"`, so `main()` never fires.

## 5.17 Checkpoint — your engine works

Now the real test. You do not have the demo folder yet, so make a quick one by
hand:

```powershell
mkdir try-it
"hello" | Out-File try-it\notes.txt
Copy-Item $env:WINDIR\Web\Wallpaper\Windows\* try-it\ -ErrorAction SilentlyContinue
```

That puts a text file and a few real wallpapers in `try-it`. Now:

```powershell
python organizer.py try-it --dry-run
```

You should see a plan grouping files into folders like `Images/` and
`Documents/`, ending with something like:

```
would move 4 file(s) into 2 folder(s).
```

Try the variations:

```powershell
python organizer.py try-it --suggest          # pattern suggestions
python organizer.py try-it                    # actually move
python organizer.py --undo                     # put them back
```

After the move, look inside `try-it` in Explorer: the files are in `Images/` and
`Documents/`. After the undo, they are back at the top level **and the empty
folders are gone**.

> **This is the moment the app exists.** Everything after this is interface.
> If your output matches, you have a working file organizer. Congratulations —
> the hard part is done.

---

# Part 6 — `gui.py`: the desktop window

Now the part you click on. We use **tkinter**, which ships with Python — nothing
to install. This file is long, but it is the *easy* kind of long: lots of small
widgets, very little logic. All the thinking already lives in `organizer.py`.

Create `gui.py`.

## 6.1 Chunk 1 — imports and colours

```python
"""A desktop window for the organizer, built with tkinter.

Tkinter ships with Python, so there is nothing to install. Everything the
command line can do, this window can do too, because it calls the same
functions in organizer.py.

Run it with:  python gui.py
"""

import threading
import time
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import config
import history
import organizer
import patterns

BG = "#0f1117"
CARD = "#171a23"
LINE = "#2b3242"
TEXT = "#e7ebf3"
MUTED = "#98a2b8"
ACCENT = "#4f8cff"
OK = "#3ecf8e"
WARN = "#f0b45a"
DANGER = "#ff6b6b"
MONO = ("Consolas", 9)
```

- `import tkinter as tk` — the window toolkit. `as tk` is a nickname, so we type
  `tk.Button` instead of `tkinter.Button` hundreds of times.
- `from tkinter import filedialog, messagebox, ttk` — three sub-toolboxes:
  `filedialog` (the "browse for a folder" dialog), `messagebox` (pop-up alerts),
  and `ttk` (the nicer-looking themed widgets).
- The colour constants are just hexadecimal colour codes with friendly names. If
  you want to change the theme later, you change one line here. **Naming your
  values instead of scattering them around is a real habit worth copying.**
- `MONO = ("Consolas", 9)` — a font as a tuple: family and size.

## 6.2 Chunk 2 — the class and its setup

```python
class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.cfg = config.load()
        self.watching = False
        self.worker = None

        root.title("Download Organizer")
        root.geometry("920x720")
        root.minsize(760, 600)
        root.configure(bg=BG)

        self._build_styles()
        self._build_header()
        self._build_tabs()
        self._refresh_all()
```

**What is a class?** A bundle of data and the functions that work on it. Here it
is "the window and everything it can do". You build it once with `App(root)`.

- `def __init__(self, root):` — a special function that runs **automatically**
  when you create the object. This is where setup happens.
- `self` — how a class refers to **itself**. `self.root = root` means "remember
  this window as my root". Every function in the class gets `self` first, and
  `self.something` is the object's own memory.
- `self.cfg = config.load()` — settings loaded **once**, kept handy.
- `self.watching = False` — are we in watch mode right now?
- `root.title(...)`, `root.geometry("920x720")`, `root.minsize(...)` — set the
  window title, its starting size, and the smallest it may be shrunk to.
- The last four lines call the builder functions. **Order matters**: styles first
  (so widgets look right), then the header, then the tabs, then fill in saved
  values.

## 6.3 Chunk 3 — the look

```python
    def _build_styles(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", background=BG, foreground=TEXT,
                        fieldbackground=CARD, font=("Segoe UI", 10))
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=CARD, foreground=MUTED,
                        padding=(16, 8), font=("Segoe UI", 10))
        style.map("TNotebook.Tab",
                  background=[("selected", LINE)],
                  foreground=[("selected", TEXT)])
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("Muted.TLabel", foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Head.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("TButton", background=LINE, foreground=TEXT,
                        borderwidth=0, padding=(12, 7), font=("Segoe UI", 10))
        style.map("TButton", background=[("active", "#39425a")])
        style.configure("Primary.TButton", background=ACCENT, foreground="white")
        style.map("Primary.TButton", background=[("active", "#3b7bef")])
        style.configure("Ok.TButton", background=OK, foreground="#07281b")
        style.map("Ok.TButton", background=[("active", "#34b87d")])
        style.configure("TCheckbutton", background=BG, foreground=TEXT)
        style.map("TCheckbutton", background=[("active", BG)])
        style.configure("Treeview", background=CARD, fieldbackground=CARD,
                        foreground=TEXT, rowheight=24)
        style.configure("Treeview.Heading", background=LINE, foreground=TEXT)
```

This is the tedious-but-easy part: telling tkinter what everything should look
like. You do not need to memorise it.

- `ttk.Style(self.root)` — the style object for this window.
- `style.theme_use("clam")` — pick a base theme. `"clam"` is the one that lets
  us recolour most things; the default Windows theme ignores some colours. The
  `try/except` is there because on the rare system where `clam` is missing, we
  still want the app to open.
- `style.configure(".", ...)` — the `.` means "apply these defaults to
everything".
- `style.configure("Primary.TButton", ...)` — **naming a style**. Any widget
  made with `style="Primary.TButton"` gets the blue look. The `.` in the middle
  is tkinter's convention for a variant of a base widget type.
- `style.map("TButton", background=[("active", "#39425a")])` — `map` sets
  colours **for a state**. `"active"` is the hover state, so buttons lighten
  when your mouse is over them.

> **Why bother?** The defaults look like Windows 95. Fifteen lines of colour
> gets you something you are happy to keep open. Skip it entirely on your first
> pass if you like — the app works without it.

## 6.4 Chunk 4 — the top bar

```python
    def _build_header(self):
        bar = tk.Frame(self.root, bg=CARD, height=58)
        bar.pack(fill="x")
        tk.Label(bar, text="  Download Organizer", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left", pady=14)
        self.status = tk.Label(bar, text="", bg=CARD, fg=MUTED,
                               font=("Segoe UI", 9))
        self.status.pack(side="right", padx=16)
```

- `tk.Frame(...)` — a **container**, an invisible box to group things.
- `.pack(fill="x")` — place it, stretching horizontally.
- The title label goes on the left (`side="left"`), the status label on the
  right (`side="right"`).
- `self.status` is kept as an attribute so other functions can change the text
  later — that is what `_set_status()` does at the bottom of the file.

**`.pack()` versus `.grid()`:** `pack` stacks widgets, `grid` places them in a
table of rows and columns. This app uses `pack` for most things and `grid` just
for the category rows.

## 6.5 Chunk 5 — the four tabs

```python
    def _build_tabs(self):
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=12, pady=12)
        self._tab_folders(nb)
        self._tab_categories(nb)
        self._tab_patterns(nb)
        self._tab_run(nb)
```

A **Notebook** is a tabbed container. `fill="both", expand=True` means it grows
when you resize the window. Each tab is made by its own function, keeping this
one readable.

## 6.6 Chunk 6 — the Folders tab

```python
    def _tab_folders(self, nb):
        tab = ttk.Frame(nb, padding=18)
        nb.add(tab, text="Folders")

        ttk.Label(tab, text="Folders", style="Head.TLabel").pack(anchor="w")
        ttk.Label(tab, text="Leave a box empty to use the default.",
                  style="Muted.TLabel").pack(anchor="w", pady=(0, 12))

        self.var_source = tk.StringVar()
        self.var_target = tk.StringVar()
        self.var_age = tk.IntVar()
        self.var_smart = tk.BooleanVar()
        self.var_cleanup = tk.BooleanVar()

        self._path_row(tab, "Watch this folder", self.var_source)
        self._path_row(tab, "Put sorted folders here", self.var_target)
```

- `nb.add(tab, text="Folders")` — attach this frame as a tab with that label.
- `anchor="w"` — align left (west).
- `pady=(0, 12)` — space above and below: 0 on top, 12 below.
- **`StringVar` / `IntVar` / `BooleanVar`** — special "variables" that belong to
  the window. A widget can be bound to one, and then you can read the user's
  input with `.get()` and set it with `.set()`. They come in one flavour per type
  of value (text, whole number, yes/no).

Continue the tab:

```python
        age_row = tk.Frame(tab, bg=BG)
        age_row.pack(fill="x", pady=(6, 0))
        ttk.Label(age_row, text="Skip files changed less than").pack(side="left")
        tk.Spinbox(age_row, from_=0, to=300, textvariable=self.var_age,
                   width=6, bg=CARD, fg=TEXT, insertbackground=TEXT,
                   relief="flat").pack(side="left", padx=6)
        ttk.Label(age_row, text="seconds ago").pack(side="left")

        ttk.Checkbutton(tab, text="Look inside archives (smart detection)",
                        variable=self.var_smart).pack(anchor="w", pady=(14, 0))
        ttk.Checkbutton(tab, text="Delete empty folders after organizing",
                        variable=self.var_cleanup).pack(anchor="w", pady=(4, 0))

        ttk.Button(tab, text="Save settings", style="Primary.TButton",
                   command=self.save_settings).pack(anchor="w", pady=18)
        ttk.Label(tab,
                  text="Tip: click Organize in the Run tab to actually move "
                       "files, or Scan to preview first.",
                  style="Muted.TLabel").pack(anchor="w")
```

- `tk.Spinbox(from_=0, to=300, textvariable=self.var_age)` — a number box with
  up/down arrows, bound to `var_age`. Note `from_` has a trailing underscore:
  `from` is a reserved word in Python, so tkinter had to dodge it. You will see
  this everywhere in tkinter.
- `ttk.Checkbutton(variable=self.var_smart)` — a tick box bound to a
  `BooleanVar`. Tick it and the variable becomes `True`.
- `command=self.save_settings` — the function to run **when clicked**. Note: no
  brackets! You are handing over the function itself, not calling it now. Writing
  `self.save_settings()` there would run it immediately and pass the result,
  which is a classic beginner bug.

Then the two helpers this tab uses:

```python
    def _path_row(self, parent, label, var):
        ttk.Label(parent, text=label).pack(anchor="w", pady=(8, 2))
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x")
        entry = tk.Entry(row, textvariable=var, bg=CARD, fg=TEXT,
                         insertbackground=TEXT, relief="flat",
                         font=("Consolas", 9))
        entry.pack(side="left", fill="x", expand=True, ipady=7)
        ttk.Button(row, text="Browse",
                   command=lambda v=var: self._browse(v)).pack(side="left",
                                                               padx=(6, 0))

    def _browse(self, var):
        chosen = filedialog.askdirectory()
        if chosen:
            var.set(chosen)
```

- `_path_row` builds a labelled text box with a Browse button, and is called
  **twice** — once for the source folder, once for the target. That is why it
  takes `parent`, `label` and `var` as inputs instead of duplicating the code.
- `insertbackground=TEXT` — the colour of the blinking text cursor.
- `command=lambda v=var: self._browse(v)` — this one needs care. A **lambda** is
  a tiny unnamed function. `v=var` stores the current `var` as a **default
  argument**, which captures its value *right now*. Without it, both buttons
  would end up browsing for the *last* variable, because the loop variable would
  have moved on. This is the classic "late binding" trap, and the `v=var` fix is
  the standard cure.
- `filedialog.askdirectory()` — pops the standard Windows folder picker and
  returns the chosen path (or an empty string if cancelled).

> **`entry` versus `ttk.Entry`:** the plain `tk` widgets and the `ttk` ones look
> different. This app uses plain `tk.Entry` for the text boxes because it can be
> recoloured more freely to match the dark theme.

## 6.7 Checkpoint — see the window

Add this temporarily at the very bottom of the file so you can look at it:

```python
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
```

(We will replace it with a proper `main()` in a moment, but this is enough now.)

Run:

```powershell
python gui.py
```

A window opens with a **Folders** tab showing two folder boxes, a number box and
two tick boxes. The other tabs are empty for now. Close it and carry on — we
fill them in next.

## 6.8 Chunk 7 — the Categories tab

```python
    def _tab_categories(self, nb):
        tab = ttk.Frame(nb, padding=18)
        nb.add(tab, text="Categories")

        ttk.Label(tab, text="Categories", style="Head.TLabel").pack(anchor="w")
        ttk.Label(tab,
                  text="Extensions per folder, comma separated. Content "
                       "detection wins when it recognises a file.",
                  style="Muted.TLabel").pack(anchor="w", pady=(0, 10))

        wrap = tk.Frame(tab, bg=BG)
        wrap.pack(fill="both", expand=True)
        canvas = tk.Canvas(wrap, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(wrap, orient="vertical", command=canvas.yview)
        self.cat_frame = tk.Frame(canvas, bg=BG)
        self.cat_frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.cat_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.cat_rows = []
        self._rebuild_categories()

        btns = tk.Frame(tab, bg=BG)
        btns.pack(fill="x", pady=(10, 0))
        ttk.Button(btns, text="+ Add category",
                   command=self._add_category).pack(side="left")
        ttk.Button(btns, text="Save settings", style="Primary.TButton",
                   command=self.save_settings).pack(side="left", padx=8)
```

This tab has **15 categories**, which is taller than the window. So we need a
scrollbar, and tkinter's scrolling is fiddly:

- A `Canvas` is a scrollable surface. We put a `Frame` (`self.cat_frame`) inside
  it, and the rows go in that frame.
- `self.cat_frame.bind("<Configure>", ...)` — `<Configure>` fires whenever the
  frame changes size. When it does, we tell the canvas how big the scrollable
  area is (`canvas.bbox("all")` is the bounding box of everything on it).
  `lambda e: ...` ignores the event argument `e`.
- `canvas.configure(yscrollcommand=scroll.set)` and
  `scroll = ttk.Scrollbar(command=canvas.yview)` — they point at each other, which
  is how the scrollbar and the canvas stay in sync. Standard boilerplate.
- `self.cat_rows = []` — an empty list we will fill with the `(name_box,
  ext_box)` pairs, so we can read them all back later.

Then the row builders:

```python
    def _rebuild_categories(self):
        for child in self.cat_frame.winfo_children():
            child.destroy()
        self.cat_rows = []
        for name, exts in self.cfg.get("categories", {}).items():
            self.cat_rows.append(self._category_row(name, ", ".join(exts)))

    def _category_row(self, name="", exts=""):
        row = tk.Frame(self.cat_frame, bg=BG)
        row.pack(fill="x", pady=3)
        name_e = tk.Entry(row, width=18, bg=CARD, fg=TEXT,
                          insertbackground=TEXT, relief="flat")
        name_e.insert(0, name)
        name_e.pack(side="left", ipady=5)
        ext_e = tk.Entry(row, bg=CARD, fg=TEXT, insertbackground=TEXT,
                         relief="flat", font=MONO)
        ext_e.insert(0, exts)
        ext_e.pack(side="left", fill="x", expand=True, padx=6, ipady=5)
        ttk.Button(row, text="✕", width=3,
                   command=lambda r=row: r.destroy()).pack(side="left")
        return (name_e, ext_e)

    def _add_category(self):
        self.cat_rows.append(self._category_row())
```

- `_rebuild_categories` clears the frame (`winfo_children()` lists the widgets,
  `.destroy()` removes each) and rebuilds one row per category from settings.
  `", ".join(exts)` turns `["jpg", "png"]` into `"jpg, png"` — the readable form.
- `_category_row` makes two text boxes and a delete button, prefills them, and
  **returns the pair** so the caller can remember them.
- `name_e.insert(0, name)` — put text into a box at position 0 (the start).
- `command=lambda r=row: r.destroy()` — "delete the row this button is in". Same
  default-argument trick as the Browse button.
- `_add_category` appends a **blank** row, which is what the "+ Add category"
  button does.

## 6.9 Chunk 8 — the Patterns tab

```python
    def _tab_patterns(self, nb):
        tab = ttk.Frame(nb, padding=18)
        nb.add(tab, text="Patterns")

        ttk.Label(tab, text="Patterns it has noticed", style="Head.TLabel").pack(
            anchor="w")
        ttk.Label(tab,
                  text="Signals shared by several downloads. Accept one and "
                       "those files get their own folder from now on.",
                  style="Muted.TLabel").pack(anchor="w", pady=(0, 10))

        ttk.Button(tab, text="Find patterns", style="Primary.TButton",
                   command=self.find_patterns).pack(anchor="w", pady=(0, 10))

        cols = ("count", "signal", "folder", "examples")
        self.tree = ttk.Treeview(tab, columns=cols, show="headings", height=8)
        for col, width, title in (("count", 60, "Files"),
                                  ("signal", 190, "Signal"),
                                  ("folder", 170, "Suggested folder"),
                                  ("examples", 320, "Examples")):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)

        ttk.Button(tab, text="Accept selected pattern",
                   command=self.accept_pattern).pack(anchor="w", pady=(10, 0))

        ttk.Label(tab, text="Accepted rules", style="Head.TLabel").pack(
            anchor="w", pady=(18, 6))
        self.rules_box = tk.Listbox(tab, bg=CARD, fg=TEXT, relief="flat",
                                    height=5, font=MONO,
                                    selectbackground=ACCENT)
        self.rules_box.pack(fill="x")
        ttk.Button(tab, text="Remove selected rule",
                   command=self.remove_rule).pack(anchor="w", pady=(8, 0))
```

- `ttk.Treeview(columns=..., show="headings")` — a **table**. `show="headings"`
  hides the useless empty first column trees normally have.
- The `for` loop sets each column's title and width in one pass — again, naming
  the data in a tuple keeps it tidy.
- `self.rules_box = tk.Listbox(...)` — a simple list of lines, one per accepted
  rule. `selectbackground` is the highlight colour when you click a line.

Then its four functions:

```python
    def find_patterns(self):
        self.save_settings(silent=True)
        source = organizer.resolve_source(self.cfg)
        if not source.is_dir():
            messagebox.showerror("Folder not found", str(source))
            return
        self._set_status("looking for patterns...")

        def work():
            files, _ = organizer.read_folder(source, self.cfg)
            self.cfg["_ext_lookup"] = organizer.build_extension_lookup(
                self.cfg.get("categories", {}))
            found = patterns.suggest(files, self.cfg)
            self.root.after(0, lambda: self._show_patterns(found))

        threading.Thread(target=work, daemon=True).start()
```

**This is the most important concept in the whole window.**

Scanning a big folder takes seconds. If we did it inside the click function, the
window would **freeze solid** until it finished — Windows would even grey it out.
So we run the work on a **background thread**:

- `def work():` — a function defined **inside** the method, holding the long job.
- `threading.Thread(target=work, daemon=True).start()` — run `work` in parallel
  with the window. `daemon=True` means the thread is killed if you close the
  window, so it can never keep the app alive in the background.
- `self.root.after(0, lambda: self._show_patterns(found))` — **the golden rule**:
  you must never touch widgets from a background thread. `root.after(0, ...)`
  means "run this back on the main thread as soon as you can". That is the safe
  handover, and it is exactly why the window stays clickable while scanning.

> **If you remember one thing about GUI programming, make it this:**
> background thread does the work, `root.after` hands the result back to the
> window. Do anything else and you get random freezes and crashes.

```python
    def _show_patterns(self, found):
        self.tree.delete(*self.tree.get_children())
        for s in found:
            self.tree.insert("", "end", values=(
                s["count"], s["signal"], s["folder"],
                ", ".join(s["examples"])))
        self._set_status(f"{len(found)} pattern(s) found")

    def accept_pattern(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Pick one", "Select a pattern first.")
            return
        values = self.tree.item(selected[0], "values")
        signal, folder = values[1], values[2]
        self.cfg.setdefault("rules", []).append(
            {"match": signal, "folder": folder})
        config.save(self.cfg)
        self._refresh_rules()
        self._set_status(f"rule saved: {signal} -> {folder}")

    def _refresh_rules(self):
        self.rules_box.delete(0, "end")
        for rule in self.cfg.get("rules", []):
            self.rules_box.insert("end", f"{rule['match']}  ->  {rule['folder']}")

    def remove_rule(self):
        selected = self.rules_box.curselection()
        if not selected:
            return
        index = selected[0]
        self.cfg["rules"].pop(index)
        config.save(self.cfg)
        self._refresh_rules()
```

- `self.tree.delete(*self.tree.get_children())` — clear the table. The `*`
  **unpacks** the list of row ids into separate arguments, because `delete` wants
  them one by one.
- `self.tree.insert("", "end", values=(...))` — add a row. `""` means "at the top
  level", `"end"` means "at the bottom of that level".
- `self.tree.selection()` — the ids of the selected rows. `values[1]` and
  `values[2]` are the signal and the folder, because that is the column order we
  set up. Values come back as **text**, which is fine here.
- `self.cfg.setdefault("rules", []).append({...})` — same idiom as in the engine:
  get or create the list, then add the new rule. Then `config.save` writes it to
  disk, so the rule survives a restart.
- `self.rules_box.curselection()` — which line is highlighted, as a tuple of
  indexes. `pop(index)` removes that rule from the list.

## 6.10 Chunk 9 — the Run tab

```python
    def _tab_run(self, nb):
        tab = ttk.Frame(nb, padding=18)
        nb.add(tab, text="Run")

        ttk.Label(tab, text="Run", style="Head.TLabel").pack(anchor="w")
        ttk.Label(tab, text="Scan is a safe preview. Organize actually moves.",
                  style="Muted.TLabel").pack(anchor="w", pady=(0, 12))

        row = tk.Frame(tab, bg=BG)
        row.pack(anchor="w")
        ttk.Button(row, text="Scan (preview)", style="Primary.TButton",
                   command=lambda: self.run(dry=True)).pack(side="left")
        ttk.Button(row, text="Organize now", style="Ok.TButton",
                   command=lambda: self.run(dry=False)).pack(side="left",
                                                             padx=8)
        ttk.Button(row, text="Undo last run",
                   command=self.undo).pack(side="left")

        self.watch_btn = ttk.Button(row, text="Start watching",
                                    command=self.toggle_watch)
        self.watch_btn.pack(side="left", padx=8)

        self.log = tk.Text(tab, bg=CARD, fg=TEXT, relief="flat", height=20,
                           font=MONO, insertbackground=TEXT)
        self.log.pack(fill="both", expand=True, pady=(14, 0))
        self.log.configure(state="disabled")
```

Four buttons and a log area.

- `command=lambda: self.run(dry=True)` — a lambda because we need to pass an
  argument. Scan calls `run(dry=True)`, Organize calls `run(dry=False)`.
- `self.watch_btn` is kept as an attribute because its **label changes** when
  watching starts and stops.
- `self.log.configure(state="disabled")` — a `Text` widget is **editable** by
  default. We disable it so the user cannot type into the log, then temporarily
  re-enable it inside `_log()` when we need to add a line.

```python
    def _log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")
```

`_log` is the helper every other function uses to write to the log: unlock, add
lines at the end, scroll to show them (`see("end")`), lock again.

```python
    def run(self, dry):
        self.save_settings(silent=True)
        source = organizer.resolve_source(self.cfg)
        if not source.is_dir():
            messagebox.showerror("Folder not found", str(source))
            return

        target = organizer.resolve_target(self.cfg, source)
        self._log(f"\n{'=== SCAN ===' if dry else '=== ORGANIZE ==='}  {source}")

        def work():
            moves, skipped, _ = organizer.plan(source, self.cfg)
            if not moves:
                self.root.after(0, lambda: self._log("  already tidy."))
            elif dry:
                self.root.after(0, lambda: self._show_moves(moves, True))
            else:
                organizer.apply_moves(moves, self.cfg, target)
                self.root.after(0, lambda: self._show_moves(moves, False))
            for name, reason in skipped:
                self.root.after(0, lambda n=name, r=reason:
                                self._log(f"  skipped {n}: {r}"))
            self.root.after(0, lambda: self._set_status("done"))

        threading.Thread(target=work, daemon=True).start()
```

**Look at how little this does.** It does not re-implement sorting at all. It
calls `organizer.plan(...)` and `organizer.apply_moves(...)` — **the exact same
functions the command line calls**. One brain, two mouths.

- `'=== SCAN ===' if dry else '=== ORGANIZE ==='` — the header tells you which
  mode ran.
- `elif dry:` — the only difference between Scan and Organize is whether we call
  `apply_moves`. That is the entire safety mechanism, and it falls straight out
  of `plan()` being separate from `apply_moves()`.
- `lambda n=name, r=reason: ...` — **the default-argument trick again**. In a
  loop, without capturing `name` and `reason` now, every lambda would use the
  *last* value by the time it ran. This is the single most common bug in
  threaded tkinter code.

```python
    def _show_moves(self, moves, dry):
        groups = {}
        for src, _dst, folder in moves:
            groups.setdefault(folder, []).append(src.name)
        for folder in sorted(groups):
            self._log(f"  {folder}/")
            for name in groups[folder]:
                self._log(f"      {name}")
        verb = "would move" if dry else "moved"
        self._log(f"  {verb} {len(moves)} file(s).")
```

The same grouping idea as `_print_moves` in the engine, but writing into the
window instead of the terminal.

```python
    def undo(self):
        restored, problems = history.undo_last()
        self._log(f"\n=== UNDO === restored {restored} file(s)")
        for problem in problems:
            self._log(f"  - {problem}")
        self._set_status("undone")
```

The Undo button is **three lines of real work** — everything hard was already
written in `history.py`. This is what good structure buys you.

```python
    def toggle_watch(self):
        if self.watching:
            self.watching = False
            self.watch_btn.configure(text="Start watching")
            self._log("\nWatching stopped.")
            self._set_status("watching stopped")
            return
        self.save_settings(silent=True)
        self.watching = True
        self.watch_btn.configure(text="Stop watching")
        self._log(f"\n=== WATCHING every "
                  f"{self.cfg.get('watch_seconds', 30)}s ===")
        self._set_status("watching")
        threading.Thread(target=self._watch_loop, daemon=True).start()

    def _watch_loop(self):
        while self.watching:
            time.sleep(int(self.cfg.get("watch_seconds", 30)))
            if not self.watching:
                break
            source = organizer.resolve_source(self.cfg)
            if not source.is_dir():
                continue
            target = organizer.resolve_target(self.cfg, source)
            moves, _skipped, _files = organizer.plan(source, self.cfg)
            if moves:
                organizer.apply_moves(moves, self.cfg, target)
                self.root.after(0, lambda: self._show_moves(moves, False))
```

- `toggle_watch` is one button doing two jobs: if already watching, stop; else
  start. Flipping `self.watching` is the flag the loop checks.
- `_watch_loop` runs on a background thread: sleep, check the flag, scan, sort
  anything new. Because the loop checks `self.watching` **after** waking, clicking
  Stop makes it exit at the next wake-up instead of instantly — a small delay
  that is worth the simplicity.

## 6.11 Chunk 10 — shared save/load

```python
    def save_settings(self, silent=False):
        if hasattr(self, "var_source"):
            self.cfg["source"] = self.var_source.get().strip() or None
            self.cfg["target"] = self.var_target.get().strip() or None
            self.cfg["min_age_seconds"] = int(self.var_age.get() or 0)
            self.cfg["smart_detection"] = bool(self.var_smart.get())
            self.cfg["cleanup_empty_folders"] = bool(self.var_cleanup.get())
        if getattr(self, "cat_rows", None):
            categories = {}
            for name_e, ext_e in self.cat_rows:
                name = name_e.get().strip()
                if not name:
                    continue
                exts = [e.strip().lower().lstrip(".")
                        for e in ext_e.get().split(",") if e.strip()]
                categories[name] = exts
            if categories:
                self.cfg["categories"] = categories
        config.save(self.cfg)
        if not silent:
            self._set_status("settings saved")
```

This reads **every widget back into the settings dictionary**, then saves it.

- `if hasattr(self, "var_source"):` — `hasattr` asks "does this object have that
  attribute yet?". Useful because `save_settings` can be called before the tabs
  are built.
- `.get().strip() or None` — read the box, trim spaces, and if the result is
  **empty** store `None` instead. That is what makes an empty box mean "use the
  default".
- Reading categories: for each row, read both boxes. Skip rows with no name. Turn
  `"jpg, png"` into `["jpg", "png"]` with `split(",")`, trimming and
  normalising each piece; `if e.strip()` drops blanks from stray commas.
- `silent=True` — save without flashing "settings saved" in the status bar, used
  when saving is a side effect of clicking another button.

```python
    def _refresh_all(self):
        self.var_source.set(self.cfg.get("source") or "")
        self.var_target.set(self.cfg.get("target") or "")
        self.var_age.set(int(self.cfg.get("min_age_seconds", 5)))
        self.var_smart.set(self.cfg.get("smart_detection", True))
        self.var_cleanup.set(self.cfg.get("cleanup_empty_folders", True))
        self._refresh_rules()
        self._log("Ready. Start with Folders, then Scan in the Run tab.")

    def _set_status(self, text):
        self.status.configure(text=text)
```

`_refresh_all` is the reverse: push saved settings **into** the widgets. `or ""`
converts a `None` source into an empty box.

## 6.12 Chunk 11 — the entry point

```python
def main():
    config.save(config.load())        # make sure config.json exists
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
```

- `config.save(config.load())` — load then immediately save, which creates
  `config.json` if it does not exist yet, so the user has a file to look at.
- `root = tk.Tk()` — create the window.
- `App(root)` — build everything inside it (our `__init__` does the work).
- `root.mainloop()` — **start listening for clicks.** Everything before this line
  *sets up* the window; `mainloop` is what keeps it on screen and responding
  until you close it. This is the last thing that runs.

## 6.13 Checkpoint — the whole app

You just replaced the temporary block from 6.7 with this proper `main()`. Run it:

```powershell
python gui.py
```

Now check, tab by tab:

1. **Folders** — boxes filled from your settings.
2. **Categories** — 15 rows, scrollable, with a working ✕ on each.
3. **Patterns** — the table and the empty rules list.
4. **Run** — the four buttons and the log.

Then test the real thing. Point the Folders tab at your `try-it` folder from
Part 5, put a few files back in it, and click **Scan (preview)**. The log should
fill with the same plan the command line gave you. Then **Organize now**, and
finally **Undo last run**.

> **Notice what just happened:** you drove the *exact same engine* from a
> window. That is the payoff of splitting the app into files. You never wrote a
> second sorter.

---

# Part 7 — the two support files

## 7.1 `run.py` — the entry point for the .exe

Seven lines. Type them exactly:

```python
"""Entry point for the built .exe.

When you package the app, this is what runs. It simply opens the desktop
window. Running from source you can still use organizer.py or gui.py directly.
"""

from gui import main

if __name__ == "__main__":
    main()
```

**Why does this exist?** PyInstaller needs **one** file to start from. If we
pointed it at `gui.py`, that would work too, but a dedicated entry file keeps the
build command simple and gives us a place to add startup code later (like a
splash screen). `from gui import main` borrows the `main()` function — and thanks
`to the `if __name__` guard in `gui.py`, importing it does **not** open a window
immediately.

## 7.2 `make_demo_files.py` — a safe playground

You cannot test a file organiser on your real Downloads folder while learning.
This file builds a fake one, full of tricky files designed to exercise every part
of the app.

```python
"""Builds a fake Downloads folder so you can try the organizer safely.

Run me, then point the organizer at the folder it makes:

    python make_demo_files.py
    python organizer.py demo_downloads --dry-run
    python organizer.py demo_downloads --suggest

It creates small but REAL archives so the pattern detection has something
honest to chew on, plus a pile of ordinary files with realistic names.
"""

import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent / "demo_downloads"
OLD = 1730000000  # old timestamp: stops the "still downloading" check skipping


def zip_file(name, contents):
    """Write a zip where contents is {inner path: bytes or str}."""
    path = ROOT / name
    with zipfile.ZipFile(path, "w") as zf:
        for inner, data in contents.items():
            if isinstance(data, str):
                data = data.encode("utf-8")
            zf.writestr(inner, data)
    os.utime(path, (OLD, OLD))


def raw(name, data):
    path = ROOT / name
    path.write_bytes(data)
    os.utime(path, (OLD, OLD))
```

- `zipfile.ZipFile(path, "w")` — create a **new** zip (`"w"` = write).
  `zf.writestr(inner, data)` writes one file inside it.
- `isinstance(data, str)` — if the content was given as text, encode it to bytes
  first, because zips store bytes.
- `os.utime(path, (OLD, OLD))` — set the file's access and modified times to an
  old timestamp. **This is important:** without it, the files would be brand new,
  and the engine's "skip files changed in the last 5 seconds" rule would skip
every one of them!

Now the files themselves. First the Minecraft-style packages, which should
self-sort and gain version subfolders:

```python
ROOT.mkdir(exist_ok=True)

# --- Minecraft-ish packages (auto-sorted, version subfolders) -------------
zip_file("sodium-fabric-1.20.1.jar", {
    "fabric.mod.json": '{"id":"sodium","depends":{"minecraft":">=1.20.1"}}',
    "sodium/Sodium.class": b"x",
})
zip_file("jei-1.20.1-forge.jar", {
    "META-INF/mods.toml": 'modLoader="javafml"',
    "mezz/jei/Jei.class": b"x",
})
zip_file("faithful-1.20.zip", {
    "pack.mcmeta": '{"pack":{"pack_format":15}}',
    "assets/minecraft/textures/block/stone.png": b"\x89PNG\r\n\x1a\n",
})
zip_file("complementary-shaders.zip", {
    "shaders/shaders/gbuffers_terrain.fsh": "// glsl",
})
```

Each one contains the **one marker file** that `_inner_signals` looks for. The
names are realistic, including the version numbers, which is what lets us test
both the pattern detection and the version-subfolder logic.

Then the patterns the app should **suggest** rather than assume:

```python
# --- Patterns the user has NOT pre-approved: should become suggestions ----
# Factorio mods: recognised by info.json inside.
for i in range(3):
    zip_file(f"space-exploration-{i}.zip", {
        "info.json": '{"name":"space-exploration"}',
        "data.lua": "return {}",
    })
# RimWorld mods: recognised by About/About.xml.
for i in range(3):
    zip_file(f"rimhud-{i}.zip", {
        "About/About.xml": "<ModMetaData/>",
        "Assemblies/RimHUD.dll": b"MZ",
    })
```

**Three of each, and that is not an accident.** The engine only suggests a
pattern when at least three files share a signal (`min_pattern_files`), so these
loops create exactly enough to trigger it. Writing the files in a loop
(`for i in range(3)`) keeps it short.

Finally, ordinary files that exercise the other rules:

```python
# --- Ordinary everyday downloads -----------------------------------------
raw("installer.msi", b"MZ" + b"\x00" * 40)          # Installers
raw("whatsapp.apk", b"PK\x03\x04" + b"\x00" * 40)   # Android
raw("JetBrainsMono.ttf", b"\x00\x01\x00\x00" + b"\x00" * 40)   # Fonts
raw("chair.glb", b"glTF" + b"\x00" * 40)            # 3D Models
raw("ubuntu-24.04.iso", b"\x00" * 80)               # Disk Images
raw("dune.epub", b"PK\x03\x04" + b"\x00" * 40)      # eBooks
raw("tweaks.sh", b"#!/bin/bash\nset -e\necho done\n")   # Scripts
raw("holiday-photo.txt", b"\x89PNG\r\n\x1a\n" + b"\x00" * 40)  # really a PNG
raw("IMG_20240115_120000.jpg", b"\xff\xd8\xff\xe0" + b"\x00" * 40)  # phone photo
raw("Screenshot 2024-05-01 180000.png",
    b"\x89PNG\r\n\x1a\n" + b"\x00" * 40)            # screenshot pattern
raw("notes.xyz", b"Just some notes I typed out.\n")  # Other
raw("bigfile.zip.part", b"PK\x03\x04partial")        # skipped

print(f"Created a demo folder at: {ROOT}")
print("Now try:  python organizer.py demo_downloads --dry-run")
print("Then:     python organizer.py demo_downloads --suggest")
```

Each `raw(...)` is a file containing the **real signature bytes** for its type,
written with the `b"..."` shorthand plus `b"\x00" * 40` to pad it out. They are
not valid files in every case — a `chair.glb` is not a real 3D model — but they
all start with the right bytes, which is exactly what we are testing.

Two of them are deliberate traps:

- `holiday-photo.txt` is really a PNG. It should land in **Images**, proving
  content beats the `.txt` name.
- `bigfile.zip.part` should be **skipped**, proving the partial-download guard.

## 7.3 Checkpoint — the full app, safely

Now run the whole thing end to end:

```powershell
python make_demo_files.py
python organizer.py demo_downloads --dry-run
python organizer.py demo_downloads --suggest
```

On the `--suggest` run, look for lines starting `3  inner:factorio-mod` and
`3  inner:rimworld-mod`. **The app worked those out on its own** — nothing in it
says "Factorio" except a name for the signal. That is the pattern engine doing
exactly what you asked for.

Now move and undo:

```powershell
python organizer.py demo_downloads
python organizer.py --undo
```

Check in Explorer that the demo folder is exactly how it started. If it is,
every single part of the app is working.

---

# Part 8 — turning it into a Windows `.exe`

Right now the app needs Python installed. An `.exe` is one file anyone can
double-click. We use **PyInstaller**.

## 8.1 Install it

```powershell
python -m pip install pyinstaller
```

`pip` is Python's package installer (`-m pip` means "run the pip module").

## 8.2 Build

In your project folder:

```powershell
python -m PyInstaller --onefile --windowed --name DownloadOrganizer run.py
```

- `--onefile` — everything in a single `.exe`.
- `--windowed` — no black console window behind the app (correct for a GUI).
- `--name DownloadOrganizer` — the output file name.
- `run.py` — the entry point from Part 7.

After a minute or two you get:

```
dist/DownloadOrganizer.exe
```

Double-click it. It opens like any Windows program, and that one file is the
whole app — copy it to a USB stick, send it to a friend, run it anywhere.

## 8.3 What PyInstaller actually did

It read your code, found every tool it uses (`import config`, `import tkinter`,
the lot), and glued them — **plus a copy of Python itself** — into one file. That
is why it is about 13 MB: it is carrying an interpreter around with it.

## 8.4 Why your settings moved

Run the `.exe`, then look here:

```powershell
explorer $env:APPDATA\DownloadOrganizer
```

That is where `config.json` and `history.json` now live. Remember `data_dir()`
from Part 2, with its `getattr(sys, "frozen", False)` check? This is it in
action. Inside a packed `.exe` there is no source folder to save into, so the app
uses `%APPDATA%` like a proper Windows program.

> **A normal warning.** Windows will probably say "unknown publisher" the first
> time, because nobody paid for a code-signing certificate. Click **More info →
> Run anyway**. Every homemade `.exe` does this.

---

# Part 9 — Git and GitHub, properly explained

Two different things, and confusing them is the usual reason beginners get stuck:

- **Git** — a program on your computer that saves versions of your work. An
  unlimited undo history for a whole folder.
- **GitHub** — a website that stores a copy of your Git projects online.

**Git is the tool. GitHub is the place.** You can use Git happily with no GitHub
at all.

## 9.1 Why you want this

- **Safety net.** Broke something? Go back to an hour ago.
- **Portfolio.** Employers and Ausbildung interviewers look at GitHub. A real
  repo you understand beats an empty CV — and you now have one.
- **Backup.** Laptop dies, code survives.

## 9.2 Install and identify yourself

Install from <https://git-scm.com/download/win> (accept the defaults), then:

```powershell
git --version
git config --global user.name "Muneeb Khan"
git config --global user.email "you@example.com"
```

Use the same email you will register on GitHub: it gets attached to every commit
(that is the word for a saved snapshot).

## 9.3 Start tracking the project

In your project folder:

```powershell
git init
```

This creates a hidden `.git` folder — Git's memory. Do not delete it, and do not
panic when you cannot see it; Explorer hides it by default.

## 9.4 The `.gitignore` file

Type this file so Git skips junk you never want online:

```
__pycache__/
*.pyc
build/
*.spec
config.json
history.json
demo_downloads/
try-it/
.vscode/
.idea/
```

Line by line:

- `__pycache__/` and `*.pyc` — compiled cache Python generates. Rebuilt
  automatically, never worth saving.
- `build/` and `*.spec` — PyInstaller's temporary files.
- `config.json`, `history.json` — **your personal settings and move history.**
  Yours are irrelevant to anyone else, and could contain private folder paths.
- `demo_downloads/`, `try-it/` — test junk.
- `.vscode/`, `.idea/` — editor settings.

> **The `dist/` folder is deliberately NOT ignored**, so your built `.exe` *is*
> included in the repo. Delete that line if you would rather not commit a 13 MB
> binary.

## 9.5 Your first commit

```powershell
git add .
git commit -m "Download organizer: engine, GUI, and docs"
```

- `git add .` — **stage** everything (the `.` means "here"). Staging means "include
  this in the next snapshot".
- `git commit -m "..."` — take the snapshot, with that message.

Messages should describe **what changed**, not "stuff". "Add undo support" is a
commit message; "changes" is not.

Useful checks:

```powershell
git status              # what has changed since the last commit
git log --oneline       # the list of commits
```

> **If Git says your identity is unknown**, you skipped 9.2. Run those two
> `git config` lines and try again.

## 9.6 Push it to GitHub

1. Make a free account at <https://github.com>.
2. Click **New repository**. Name it `download-organizer`. **Do not** tick "Add a
   README" or ".gitignore" — you already made those. Click Create.
3. GitHub shows a URL like
   `https://github.com/yourname/download-organizer.git`.

Then, in your project folder:

```powershell
git remote add origin https://github.com/yourname/download-organizer.git
git branch -M main
git push -u origin main
```

- `git remote add origin <url>` — tell Git where the online copy lives. `origin`
  is just a nickname for that URL.
- `git branch -M main` — rename your branch to `main`, GitHub's default name.
- `git push -u origin main` — upload your commits. The `-u` pairs your folder
  with that remote, so afterwards a bare `git push` is enough.

Refresh the GitHub page: your seven files are there. **That is a real repository,
and it is yours.**

## 9.7 The everyday rhythm

From now on it is always these three commands:

```powershell
git add .
git commit -m "Describe what you changed"
git push
```

Small, frequent commits beat one giant one. Commit every time something works.

## 9.8 Passwords, tokens, and the thing that confuses everyone

GitHub no longer accepts your account password for `git push`. You need a
**Personal Access Token**:

1. On GitHub: your picture → **Settings** → **Developer settings** → **Personal
   access tokens** → **Tokens (classic)** → **Generate new token**.
2. Give it a name, tick the **repo** box, generate, and **copy the token now** —
   GitHub will not show it again.
3. When Git asks for a password, paste the **token** instead.

Windows remembers it after the first time. (SSH keys are a tidier alternative,
but the token route is the right first step.)

> **Never paste your token into code or a chat.** Treat it like a password. If
> you ever leak one, delete it on GitHub immediately — this is exactly why we
> put `config.json` in `.gitignore`, incidentally; that is where private paths
> and settings live.

## 9.9 Two more commands worth knowing

**Clone** — download someone else's project:

```powershell
git clone https://github.com/someone/their-project.git
```

**Discard my uncommitted edits** — put files back to the last commit:

```powershell
git restore .
```

Careful: that throws away uncommitted work. It is your undo, but only for things
you never committed.

> **The whole of daily Git, in one paragraph.** `git add .` picks what to
> include. `git commit -m "..."` saves the snapshot locally. `git push` uploads
> it to GitHub. That is 90% of it.

---

# Part 10 — When things go wrong

**`python is not recognized`**
The PATH checkbox was missed. Reinstall Python with "Add python.exe to PATH"
ticked.

**`ModuleNotFoundError: No module named 'config'`**
You are running the file from the wrong folder. `cd` into your project folder
first — Python looks for `import config` in the folder you are standing in.

**`SyntaxError: invalid syntax` pointing at a line you just typed**
Almost always a missing `)`, `]` or `}`, or a missing quote. Count the brackets on
the lines above. The error often shows up *after* the real mistake.

**`IndentationError: unexpected indent`**
You mixed tabs and spaces, or used 2 spaces instead of 4. Select the whole file
and re-indent consistently with 4 spaces.

**`PermissionError` when moving a file**
The file is open in another program, or still downloading. Close it and retry.
The app also skips recently-changed files for exactly this reason.

**The window freezes when I click Scan**
You ran the work on the main thread instead of a background one. Check that the
job is inside `def work():` and started with `threading.Thread(...).start()`, and
that widget updates go through `self.root.after(0, ...)`.

**A file went to the wrong folder**
That is feedback, not a bug. Add a rule in the Patterns tab, or add the missing
extension to the right category. The app is designed to be taught.

**The `.exe` says "Windows protected your PC"**
Normal for unsigned homemade programs. More info → Run anyway.

**`fatal: not a git repository`**
You ran a Git command outside your project folder. `cd` into it first.

**I messed up my files**
Click **Undo last run**, or run `python organizer.py --undo`. In future, always
`--dry-run` first — that is what it is for.

---

# Part 11 — What you have, and where to go next

## 11.1 The files you built

```
download-organizer/
├── config.py            settings + where files are stored
├── patterns.py          signals: what a file really is
├── history.py           undo
├── organizer.py         the engine + command line
├── gui.py               the desktop window
├── run.py               entry point for the .exe
├── make_demo_files.py   safe test folder
├── .gitignore
└── dist/DownloadOrganizer.exe
```

## 11.2 What you actually learned

- **Bytes** — every file type starts with a signature, so you can identify a file
  no matter what it is called.
- **Sets and dictionaries** — the right container for the job: unordered
  membership versus labelled lookup.
- **Signals and patterns** — measuring small facts, then letting *frequency* turn
  them into a suggestion nobody had to hard-code.
- **Separation of concerns** — `plan()` decides, `apply_moves()` acts. That one
  split gives you dry runs, previews and undo.
- **Layered safety** — skip partial files, skip fresh files, never overwrite,
  never delete a folder you did not create.
- **Two front ends, one engine** — the terminal and the window call the same
  functions, so behaviour can never drift apart.
- **Threads and `root.after`** — keep a window responsive while real work happens.
- **Packaging** — turning Python into an `.exe` anyone can run.
- **Git and GitHub** — snapshots, remotes, `.gitignore`, tokens.

## 11.3 Honest next steps

Small and satisfying:

- **Duplicate finder** — same size *and* same start bytes usually means the same
  file. Flag them instead of moving.
- **A run log** — append every moved file to a text file so you have a permanent
  record, not just the last 20 runs.
- **More signals** — add a line to `_inner_signals` and a name to
  `FRIENDLY_FOLDERS` for any game or program you care about.

Bigger:

- **A tray icon** so watch mode runs quietly in the background.
- **A settings export/import** so you can share your rules.
- **Per-folder rules** (unlike per-signal rules) for people who want to say
  "PDFs from this website go here".

## 11.4 The habit that matters

You did not copy-paste this app. You built it, chunk by chunk, and checked each
piece before moving on. That is the actual skill — the same one that will carry
you through an Ausbildung, and through any language or framework afterwards.

**Build the smallest thing that works. Add one idea. Prove it. Repeat.**

Everything else is detail.
