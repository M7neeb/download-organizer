# Build the Download Organizer — a beginner's guide

Hi. This is the long, slow, everything-explained version. If you follow it from
the top you will build this whole app yourself, and you will understand every
line. No prior Python needed — if you can follow a recipe, you can do this.

We build it in stages. Each stage is a small working program you can run before
moving on. At the end we turn it into a Windows `.exe` and put it on GitHub.

**Read the "What just happened?" boxes.** They explain the *why*, which is the
part that actually teaches you something.

## What we are making

A program that tidies your Downloads folder. It sorts files into folders like
`Images`, `Videos`, `Installers` — but instead of only trusting the file name,
it **opens each file and looks at what is really inside**.

The clever bit is the final stage: when several downloads share something
unusual (they are all Factorio mods, all screenshots, all Android apps), the
program notices the pattern and *suggests* giving them their own folder. You
approve it once and it remembers. Nothing about Minecraft or any other game is
hard-coded — it learns from whatever is in *your* downloads.

## Table of contents

- Part 0 — Plain-English glossary (read this even if you skip nothing else)
- Part 1 — Install Python and set up your workspace
- Part 2 — Stage 1: the simplest possible sorter
- Part 3 — Stage 2: reading a file's real type (magic bytes)
- Part 4 — Stage 3: reading a file's text
- Part 5 — Stage 4: the pattern idea (signals)
- Part 6 — Stage 5: suggesting folders
- Part 7 — Stage 6: filters and safety
- Part 8 — Stage 7: letting the user choose (command line)
- Part 9 — Stage 8: settings that survive a restart
- Part 10 — Stage 9: watch mode
- Part 11 — Stage 10: undo
- Part 12 — Stage 11: the desktop window
- Part 13 — Stage 12: turning it into a Windows .exe
- Part 14 — Git and GitHub, explained properly
- Part 15 — When things go wrong (troubleshooting)
- Part 16 — The complete file map (answer key)

This tutorial builds a working app with every feature the finished one has — you
write your own version, with your own names and a simpler window. Part 16 is a
side-by-side map of "what the tutorial calls it" versus "what the finished code
calls it", so you can always find your way around the real files.

---

# Part 0 — Plain-English glossary

You will see these words constantly. Here is what they mean, in your language.

**Terminal / console / PowerShell / command prompt.** A window where you type
commands instead of clicking. On Windows, press the Start button and type
`PowerShell`. It opens a blue-ish window. You type a line, press Enter, it does
something.

**Command.** A line you type in the terminal. Example: `python --version`. The
first word is the program, the rest are instructions to it.

**Python.** A programming language. You write instructions in a text file, then
tell Python to run that file.

**Script / program / code.** All mean "a text file of Python instructions".

**`.py` file.** A Python file. `organizer.py` is one.

**Function.** A named block of instructions you can run by saying its name.
`print("hi")` runs the built-in function `print`. You make your own with `def`:

```python
def greet(name):
    print("Hello", name)

greet("Muneeb")     # prints: Hello Muneeb
```

- `def` means "I am defining a function".
- `name` in the brackets is an *input* (a "parameter").
- The indented lines (4 spaces) are the function's body. **Indentation is not
  decoration in Python — it is how Python knows what belongs inside the
  function.** Use exactly 4 spaces, never a Tab.
- `return` sends a value back out. `print` just shows it.

**Variable.** A named box holding a value. `age = 5` puts 5 in the box `age`.

**String.** Text, in quotes: `"hello"`. **Integer**: a whole number, `5`.
**List**: an ordered collection, `["a", "b"]`. **Dictionary**: named boxes,
`{"jpg": "Images"}` — look up `"jpg"` and you get `"Images"`.

**Import.** Borrowing tools someone else wrote. `import os` loads Python's "os"
toolbox. `from pathlib import Path` loads just one tool from a toolbox.

**Error / traceback.** When Python cannot do something, it prints a wall of red
text called a traceback. Read the **last line** first — that is the actual
problem. The lines above show where it happened.

**Byte.** One unit of raw data. A file is millions of bytes. `b"\x89PNG"` means
"I mean these exact raw bytes", the `b` standing for "bytes".

---

# Part 1 — Install Python and set up

## 1.1 Install Python

1. Go to <https://www.python.org/downloads/> and download the latest Python for
   Windows.
2. Run the installer. **On the first screen, tick the checkbox that says "Add
   python.exe to PATH".** This matters a lot — it lets you type `python` in the
   terminal. If you miss it, re-run the installer and choose "Modify".
3. Click through and finish.

Now open PowerShell (Start button → type `PowerShell`) and type:

```powershell
python --version
```

You should see something like `Python 3.13.1`.

> **What just happened?** You ran the program `python` and gave it the
> instruction `--version`, which means "tell me your version". If instead you
> see `python : The term 'python' is not recognized`, the PATH checkbox was
> missed — reinstall with it ticked.

## 1.2 Make a project folder

In PowerShell:

```powershell
cd ~
mkdir download-organizer
cd download-organizer
```

- `cd ~` means "change directory to my home folder". `~` is shorthand for your
  user folder.
- `mkdir` makes a new folder.
- The second `cd` moves you *into* it.

To check where you are, type `pwd` (print working directory) or `cd` alone.

## 1.3 Get a proper editor

Download **Visual Studio Code** (free) from <https://code.visualstudio.com/>.
This is where you will write code. Install it, then in PowerShell type:

```powershell
code .
```

The `.` means "this folder". A window opens showing your empty project.

> **Why not Notepad?** Notepad works, but VS Code colours your code, shows
> mistakes, and has a built-in terminal (menu: Terminal → New Terminal) so you
> can run code without switching windows. It is the tool professionals use.

You are ready. Every stage below is: make a `.py` file, paste the code, run it.

---

# Part 2 — Stage 1: the simplest possible sorter

We start with a deliberately dumb version that only looks at file names. It
works, and it gives us a base to build on.

Make a file called `stage1.py` and put this in it:

```python
# Stage 1: sort by extension only.

from pathlib import Path      # tools for working with file paths
import shutil                 # tools for moving files

EXTENSIONS = {
    "jpg": "Images",
    "png": "Images",
    "mp3": "Audio",
    "wav": "Audio",
    "pdf": "Documents",
    "txt": "Documents",
    "mp4": "Videos",
}


def sort_folder(folder_path):
    folder = Path(folder_path)          # turn the text into a real path object

    for item in folder.iterdir():       # go through everything in the folder
        if not item.is_file():          # skip subfolders
            continue

        ext = item.suffix.lstrip(".").lower()     # ".JPG"  ->  "jpg"
        target_name = EXTENSIONS.get(ext, "Other")  # find its folder
        target_folder = folder / target_name        # build the full path

        target_folder.mkdir(exist_ok=True)          # create it if missing
        shutil.move(str(item), str(target_folder / item.name))
        print("moved", item.name, "->", target_name)


sort_folder("test-downloads")
```

## 2.1 Make something to sort

In PowerShell:

```powershell
mkdir test-downloads
```

Then drop a few junk files in that folder (any random files from your computer
— a photo, a PDF, whatever). It does not matter what.

## 2.2 Run it

```powershell
python stage1.py
```

Now open `test-downloads` in File Explorer. You will see folders called
`Images`, `Audio`, and so on, with files inside.

## 2.3 What just happened? (line by line)

- `from pathlib import Path` — `Path` is Python's way of handling file paths.
  The big win: `folder / "Images"` builds a correct path on any computer, so
  you never have to worry about `/` versus `\`.
- `for item in folder.iterdir():` — `iterdir()` hands you each thing in the
  folder one at a time. The `for` loop repeats the indented block for each one.
- `if not item.is_file(): continue` — `is_file()` is `True` for files and
  `False` for folders. `continue` means "skip the rest of this loop and go to
  the next item", so we never touch folders.
- `item.suffix` gives the extension *with* the dot: `.jpg`. `.lstrip(".")`
  removes the dot → `jpg`. `.lower()` makes it lowercase so `.JPG` still
  matches.
- `EXTENSIONS.get(ext, "Other")` looks up `ext`. If it is not in the dictionary,
  `.get` returns `"Other"` instead of crashing. **This is an important habit:
  always give a fallback.**
- `target_folder.mkdir(exist_ok=True)` creates the folder. `exist_ok=True` means
  "if it is already there, don't complain".
- `shutil.move(source, destination)` moves the file. It wants text paths, so we
  wrap with `str(...)`.
- `print(...)` tells you what happened.

Notice `def sort_folder(folder_path):` — we made a function. The last line calls
it. We could call it twice with different folders.

**This is a real program.** Now let's make it smart.

---

# Part 3 — Stage 2: reading a file's real type

The file name lies. People rename things. So instead of trusting `holiday.jpg`,
we open the file and read its **first few bytes**.

Every file type starts with a special signature:

| File type | Starts with |
|---|---|
| PNG image | `\x89PNG` |
| JPEG image | `\xff\xd8\xff` |
| PDF | `%PDF` |
| Zip (and .jar, .apk, .docx…) | `PK\x03\x04` |
| Windows .exe | `MZ` |

Make `stage2.py`:

```python
# Stage 2: read the first bytes of a file to find its real type.

from pathlib import Path


def read_start(path, how_many=32):
    """Return the first `how_many` bytes of a file."""
    try:
        with open(path, "rb") as f:        # "rb" = read, binary
            return f.read(how_many)
    except OSError:
        return b""                          # e.g. file locked; give up quietly


def sniff_type(start):
    """Guess a file's type from its starting bytes. None means 'no idea'."""
    if start.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image"
    if start.startswith(b"\xff\xd8\xff"):
        return "image"
    if start.startswith(b"%PDF"):
        return "document"
    if start.startswith(b"PK\x03\x04"):
        return "archive"
    if start.startswith(b"MZ"):
        return "executable"
    return None


# --- quick test ---
for name in ["test-downloads"]:
    folder = Path(name)
    if folder.is_dir():
        for item in folder.iterdir():
            if item.is_file():
                kind = sniff_type(read_start(item))
                print(f"{item.name:45} -> {kind}")
```

Run it:

```powershell
python stage2.py
```

## 3.1 Try the magic trick

Find any PNG image on your computer. Copy it into `test-downloads` and **rename
it to `secret.txt`**. Run `stage2.py` again. It still reports `image`.

> **What just happened?** The bytes do not care what the file is called. That is
> the entire idea behind "content detection", and it is why this app is better
> than a plain extension sorter.

## 3.2 New things explained

- `open(path, "rb")` opens the file for reading in **binary** mode. Without the
  `b`, Python would try to read it as text and choke on pictures.
- `f.read(32)` reads up to 32 bytes. The `with ... as f:` block closes the file
  automatically when done — good practice that stops files being left locked.
- `b"\x89PNG"` — the `b` marks these as **bytes**, not text. `\x89` is a byte
  written in hex, used because it is not a normal typable character.
- `start.startswith(...)` asks "do these bytes begin with this?".
- `try:` / `except OSError:` — attempt something risky; if it fails, do the
  fallback instead of crashing. Here, if a file is locked by another program,
  we hand back empty bytes.
- `return None` — "I do not recognise this". `None` is Python's word for
  "nothing".

## 3.3 Merge into the sorter

In `stage1.py`, replace the extension lookup with: try magic bytes first, and
only fall back to the extension if that returned `None`.

```python
kind = sniff_type(read_start(item))
if kind == "image":
    target_name = "Images"
elif kind == "document":
    target_name = "Documents"
elif kind == "archive":
    target_name = "Archives"
elif kind == "executable":
    target_name = "Installers"
else:
    target_name = EXTENSIONS.get(ext, "Other")     # the old, name-based guess
```

Now a PNG renamed to `.txt` goes to `Images`. Stage 2 done.

---

# Part 4 — Stage 3: reading a file's text

Magic bytes work great — when we know the signature. A plain text file has no
signature. So for those we read the *words* and look for clues.

```python
# Stage 3: for text files, guess from the content.

TEXT_ENDINGS = {"txt", "md", "py", "js", "html", "css", "json", "csv"}

CODE_CLUES = (
    "#!/usr/bin/env python", "#include", "import ", "def ", "class ",
    "function ", "const ", "let ", "var ", "<?php",
)


def sniff_text(path):
    """Read the beginning of a file and guess what kind of text it is."""
    try:
        with open(path, "rb") as f:
            raw = f.read(8192)          # first 8 KB is plenty
    except OSError:
        return None

    # Real text has no zero bytes. Binary files are full of them.
    if b"\x00" in raw:
        return None

    text = raw.decode("utf-8", errors="ignore").lower()

    if any(clue in text for clue in CODE_CLUES):
        return "Code"
    if "<html" in text or "<!doctype html" in text:
        return "Code"
    if text.lstrip().startswith(("{", "[")):
        return "Code"                   # looks like JSON data

    return None
```

## 4.1 The two important tricks

**The zero-byte check.** `b"\x00"` is a zero byte. Text files never contain one;
pictures, videos and zip files are full of them. We test for that **before**
pretending the file is text. Without it, we would try to "read" a movie file as
words and get nonsense.

**`errors="ignore"`.** When turning bytes into text, some bytes might not be
valid characters. This tells Python to skip those instead of crashing.

`any(clue in text for clue in CODE_CLUES)` is a compact way to say "if **any**
of these clues appears in the text". It is like a mini `for` loop.

> **Idea to remember:** `any(...)` stops at the first hit. `all(...)` needs every
> one. Both read beautifully once you get used to them.

## 4.2 Try it

Make two files in `test-downloads`: one called `hello.txt` containing
`print("hi") and some code`, and one called `story.txt` containing normal
sentences. Run the sniffer. The first says `Code`; the second says `None`
(meaning "just ordinary text").

In the finished project the "is this text at all?" check is its own small helper
called `_looks_like_text()` (in `patterns.py`): it reads a couple of kilobytes
and returns True when there is no zero byte. The finished app then lets the
content signals and the extension finish the job. The `CODE_CLUES` idea above is
a neat extra you can add yourself if you want `.txt` files full of code to land
in `Code`.

---

# Part 5 — Stage 4: the pattern idea

Now the heart of the app. This is the part you asked for: *don't hard-code a
Minecraft folder — recognise patterns and suggest folders.*

## 5.1 The insight

Imagine five files in Downloads:

- `space-exploration.zip`
- `krastorio.zip`
- `bobs-mods.zip`

On their own, nothing in common. But open them, and **every one contains a file
called `info.json`**. That is not a coincidence — `info.json` is how Factorio
mods are packaged. That shared trait is a **pattern**.

We call that trait a **signal** — a small fact we measured about a file:

- `inner:info.json` — "inside this archive there is `info.json`"
- `ext:zip` — "its name ends in .zip"
- `name:invoice` — "the name contains the word invoice"
- `prefix:IMG_` — "the name starts with IMG_"

A signal on its own is boring. **A signal shared by several files is a hint that
they belong together.**

## 5.2 Building it

Here is a trimmed version. Make `stage4_patterns.py`:

```python
# Stage 4: work out the signals for a file.

import zipfile
from pathlib import Path


def look_inside(path):
    """Return the set of file names inside a zip, lower-cased."""
    try:
        with zipfile.ZipFile(path) as zf:
            return {n.lower() for n in zf.namelist()}
    except (zipfile.BadZipFile, OSError):
        return set()          # not a zip, or unreadable -> empty set


def inner_signals(names):
    found = set()
    if "info.json" in names:
        found.add("inner:factorio-mod")
    if "about/about.xml" in names:
        found.add("inner:rimworld-mod")
    if "fabric.mod.json" in names:
        found.add("inner:minecraft-mod")
    if "androidmanifest.xml" in names:
        found.add("inner:android-app")
    return found


def analyze(path):
    """All the signals for one file."""
    result = set()
    name = path.name.lower()
    ext = path.suffix.lstrip(".").lower()

    result.add(f"ext:{ext}")

    if ext in {"zip", "jar", "apk"}:
        result |= inner_signals(look_inside(path))

    if "screenshot" in name:
        result.add("name:screenshot")

    return result


# --- test it ---
folder = Path("demo_downloads")
for item in sorted(folder.glob("*.zip")):
    print(item.name, "->", sorted(analyze(item)))
```

(If you have not made `demo_downloads` yet, run
`python make_demo_files.py` first — it comes with the project and builds a safe
fake folder full of these files.)

## 5.3 New things explained

- `zipfile.ZipFile(path)` opens a `.zip` archive. `zf.namelist()` gives the list
  of files *inside* it. This is how we "look inside" a file.
- `{n.lower() for n in zf.namelist()}` is a **set comprehension** — the curly
  braces build a *set* (a bag of unique items) instead of a list. We use a set
  because we only care whether something is present, not how many times.
- `found.add(...)` puts one item into a set. `result |= other` merges one set
  into another (`|=` means "add everything from the right").
- `folder.glob("*.zip")` lists every file ending in `.zip`. The `*` means
  "anything".

## 5.4 Counting patterns

Signals alone are not enough — we only suggest a folder when **several** files
share a signal. So we count:

```python
def suggest(files, minimum=3):
    counts = {}
    for path, signals in files:
        for signal in signals:
            counts[signal] = counts.get(signal, 0) + 1

    return [s for s, count in counts.items() if count >= minimum and s.startswith("inner:")]
```

`counts.get(signal, 0) + 1` means "whatever the count is so far, add one". This
is the classic way to count things in Python.

Now run it on your `demo_downloads` folder and you will see it propose
`inner:factorio-mod` and `inner:rimworld-mod` **without anyone telling it those
exist**. That is the pattern engine.

## 5.5 Turning signals into folder names

A signal like `inner:factoriomod` is ugly. We want "Factorio Mods". So we keep a
translation table:

```python
FRIENDLY = {
    "inner:factorio-mod": "Factorio Mods",
    "inner:rimworld-mod": "RimWorld Mods",
    "name:screenshot": "Screenshots",
}

def friendly_name(signal):
    if signal in FRIENDLY:
        return FRIENDLY[signal]
    # otherwise improvise a name from the signal itself
    part = signal.split(":", 1)[1]
    return part.replace("-", " ").title()
```

`.split(":", 1)` cuts the signal into two at the first colon, and `.title()`
turns `"factorio mod"` into `"Factorio Mod"`.

**The key point: adding a new known pattern is just one new line in a
dictionary** — data, not code. That is why this design is good.

In the finished project all of this lives in `patterns.py`, and the pieces have
names you can search for:

- `MAGIC_TYPES` — the bytes table (PNG, PDF, MZ, …), used by `magic_type()`.
- `_looks_like_text()` — the zero-byte check for "is this text at all?".
- `NAME_KEYWORDS` / `NAME_PREFIXES` — the word and prefix tables
  (`screenshot`, `IMG_`, `DSC_`, …).
- `_inner_signals()` — everything that looks *inside* a zip.
- `analyze()` — runs all of the above for one file.
- `signals()` — flattens one file's results into signal strings.
- `friendly_folder()` — turns a signal into a folder name.
- `FRIENDLY_FOLDERS` — the table of nice names for known signals.
- `suggest()` — counts signals and proposes folders.

---

# Part 6 — Stage 5: suggesting folders (and accepting them)

A suggestion is only useful if the user can say "yes". So we store accepted
patterns as **rules** and check them first.

The rule is just a dictionary:

```python
{"match": "inner:factorio-mod", "folder": "Factorio Mods"}
```

`match` is the signal; `folder` is where those files should go.

When classifying a file, the order of decisions is:

1. Does a **rule** match a signal on this file? → use that folder.
2. Does an **automatic signal** match? (screenshots, Android apps, …) → use that.
3. What does the **bytes** say the type is? → Images, Videos, …
4. Fall back to the **extension** from our settings.

First match wins. That is the whole priority system — just the order of a few
`if` checks. Here is the idea in code:

```python
def classify(path, signals, rules, auto):
    for rule in rules:                        # 1. user rules
        if rule["match"] in signals:
            return rule["folder"]

    for signal, folder in auto.items():       # 2. automatic patterns
        if signal in signals:
            return folder

    return None                               # 3/4: let the type/extension decide
```

> **Why do rules come first?** Because the user is always right. If you told the
> app "RimWorld mods go in `Games/RimWorld`", that beats every automatic guess.

A file can carry several signals at once, so "which one wins?" needs an answer.
The finished app gives each *kind* of signal a rank and picks the highest:

```python
SIGNAL_PRIORITY = {"inner": 4, "name": 3, "prefix": 3, "ext": 2,
                   "type": 1, "version": 0}
```

`inner` (found by really opening the file) always beats `name` (a guess from the
filename). That helper is `_best_match()` in `organizer.py`, and the automatic
patterns live in the `AUTO_SIGNALS` dictionary — the same "data, not code" idea
as `FRIENDLY_FOLDERS`, so adding an automatic pattern is one line.

The version subfolder comes from `_pick_version()`: it collects every
`version:` signal on the file and takes the **last** one. Why last? Because mod
file names often look like `jei-15.2.1-1.20.1.jar` — the mod's own version comes
first and the game version comes last, so the last match is the reliable one.

---

# Part 7 — Stage 6: filters and safety

A real Downloads folder has traps. Three guards keep you out of trouble.

## 7.1 Ignore half-finished downloads

Browsers save a file as something like `movie.mp4.crdownload` while it is
downloading, then rename it when done. If we move the partial file, we break the
download.

```python
PARTIAL = {".part", ".crdownload", ".tmp", ".download"}

if item.suffix.lower() in PARTIAL:
    continue
```

## 7.2 Ignore files written seconds ago

Sometimes the ending is already right but the file is still being written. We
check how long ago it was changed:

```python
import time

age = time.time() - item.stat().st_mtime      # mtime = time last modified
if age < 5:                                   # changed less than 5s ago
    continue
```

`item.stat().st_mtime` is the last-modified time as a number (seconds). Subtract
it from the current time and you get the age in seconds.

## 7.3 Never overwrite

If `Downloads/Images/photo.jpg` already exists and a *different* `photo.jpg`
arrives, we must not silently destroy the first one.

```python
def free_name(folder, filename):
    destination = folder / filename
    if not destination.exists():
        return destination

    stem = destination.stem          # "photo"
    suffix = destination.suffix      # ".jpg"
    number = 1
    while True:
        candidate = folder / f"{stem} ({number}){suffix}"
        if not candidate.exists():
            return candidate
        number += 1
```

Now the second one becomes `photo (1).jpg`, then `photo (2).jpg`.

> **`while True:` with a `return` inside** is the standard "search until you find
> it" pattern. It would loop forever without the `return` — that is what breaks
> the loop.

`f"{stem} ({number}){suffix}"` is an **f-string**: text with `{}` holes that get
filled in. `f"a{1+1}b"` gives `a2b`. You will use these constantly.

In the finished project these three guards are collected into one function,
`looks_like_download()` — it returns `(ok, reason)` so the caller knows *why*
something was left alone and can print it. The renaming helper is
`unique_destination()`, and the function that walks the folder and analyses each
file is `read_folder()`.

---

# Part 8 — Stage 7: letting the user choose

Editing the code to change folders is silly. Real programs take **arguments**.

```python
import argparse

parser = argparse.ArgumentParser(description="Organize downloads")
parser.add_argument("source", nargs="?",
                    help="folder to organize (default: Downloads)")
parser.add_argument("--dry-run", action="store_true",
                    help="show what would happen, change nothing")
parser.add_argument("--watch", type=int, metavar="SECONDS",
                    help="re-scan every SECONDS seconds")
args = parser.parse_args()

print("source:", args.source)
print("dry run?", args.dry_run)
print("watch every:", args.watch)
```

Now:

```powershell
python stage7.py
python stage7.py C:/some/folder
python stage7.py --dry-run
python stage7.py --watch 30
```

- `nargs="?"` means the argument is optional.
- `action="store_true"` makes `--dry-run` a simple on/off flag that becomes
  `True` when present.
- `type=int` converts the value after `--watch` from text to a number.

**`--dry-run` is the most important flag in this whole app.** It means "tell me
what you *would* do, but do not touch anything". Any program that moves or
deletes files should have one. It lets you find out it is about to do something
dumb *before* it does.

In the real project, `--dry-run`, `--watch`, `--suggest`, `--accept` and
`--undo` all work like this. Look at `main()` in `organizer.py`.

---

# Part 9 — Stage 8: settings that survive a restart

If the user picks a folder, that choice should stick. We save settings in a JSON
file.

**JSON** is a way to store data as text — lists, text, numbers and nested
dictionaries. Python can turn its dictionaries into JSON and back:

```python
import json
from pathlib import Path

CONFIG_FILE = Path(__file__).with_name("config.json")


def load_settings():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return {"source": None, "rules": []}       # defaults


def save_settings(settings):
    CONFIG_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")
```

- `Path(__file__)` is the path of *this* script. `with_name("config.json")`
  swaps the file name, so `config.json` always sits next to the script no matter
  where you run it from.
- `json.loads(text)` turns text into a Python dictionary. `json.dumps(data)`
  does the reverse. `indent=2` makes the saved file readable.
- `encoding="utf-8"` makes sure special characters work.

> **`with_name` vs `parent`:** `path.parent` is the folder, `path.with_name("x")`
> replaces the last part. Knowing these two saves a lot of string juggling.

One extra trick from the real project: when the app runs as a built `.exe`,
saving next to the script is impossible (the script is packed inside the exe),
so we save to `%APPDATA%\DownloadOrganizer` instead. That is what `data_dir()` in
`config.py` handles.

---

# Part 10 — Stage 9: watch mode

"Watch mode" means: keep running, check the folder every so often, sort whatever
appears. The core is a loop with a sleep:

```python
import time

while True:
    sort_once()
    time.sleep(30)          # wait 30 seconds, then do it again
```

That is genuinely it — but we add one nicety: letting **Ctrl+C** stop it
cleanly instead of dumping an error.

```python
try:
    while True:
        sort_once()
        time.sleep(30)
except KeyboardInterrupt:          # raised when you press Ctrl+C
    print("Stopped.")
```

> **Careful:** `time.sleep()` pauses the program for that many seconds. If you
> set a tiny number like `0.01`, the loop will run thousands of times a second
> and hammer your disk. 30 seconds is sensible.

In the real app, watch mode lives in the command line (`--watch 30`) and as the
**Start watching** button in the window. The button does the waiting on a
*background thread* so the window keeps responding while it waits — but that is
a bonus topic, not something you need yet.

---

# Part 11 — Stage 10: undo

An undo button sounds magic. It is not. It is just a **list of what we did**.

Before moving each file, we write down two things: where it came from and where
it went. Save that list to a file. To undo, read the list backwards and swap the
two paths.

```python
import json
from pathlib import Path

HISTORY = Path(__file__).with_name("history.json")


def remember(moves):
    """moves is a list of (from_path, to_path)."""
    if not moves:
        return
    runs = []
    if HISTORY.exists():
        runs = json.loads(HISTORY.read_text(encoding="utf-8"))
    runs.append([[str(a), str(b)] for a, b in moves])
    HISTORY.write_text(json.dumps(runs, indent=2), encoding="utf-8")


def undo_last():
    if not HISTORY.exists():
        return 0
    runs = json.loads(HISTORY.read_text(encoding="utf-8"))
    if not runs:
        return 0

    last = runs.pop()                 # take off the most recent run
    restored = 0
    for old_path, new_path in reversed(last):     # backwards, to be safe
        old, new = Path(old_path), Path(new_path)
        if new.exists():
            new.replace(old)          # "replace" MOVES new back onto old
            restored += 1

    HISTORY.write_text(json.dumps(runs, indent=2), encoding="utf-8")
    return restored
```

- `runs.pop()` removes and returns the last item of a list.
- `reversed(last)` walks the list from the end. We undo in reverse order so
  everything unwinds cleanly.
- `Path.replace(target)` moves a file, overwriting the target if it exists. That
  is exactly what "put it back" means.

> **Why keep a list of runs, not just one?** So you can undo the last run, and
> if you change your mind, undo the one before. The real app keeps the last 20
> runs and trims the rest so the file cannot grow forever.

This is `history.py` in the real project. The window's **Undo last run** button
just calls `history.undo_last()`.

Undo also tidies up after itself. When files move back out of `Images/`, that
folder is now empty and pointless, so it gets removed — but only if it is
genuinely empty, and never above the folder you started in:

```python
def _prune_empty_parents(folder, stop_at):
    while folder not in stop_at:
        if not folder.is_dir() or any(folder.iterdir()):
            break                       # not empty -> stop
        folder.rmdir()
        folder = folder.parent          # climb up and try the next one
```

`any(folder.iterdir())` is True if the folder has even one thing in it. The
`stop_at` set holds the folders the files came from, so we can never delete your
actual Downloads folder by mistake. And `rmdir()` only works on empty folders —
a second safety net, because it refuses to delete anything with files inside.

---

# Part 12 — Stage 11: the desktop window

Now the bit you asked for: a real Windows app with clickable tabs. We use
**tkinter** — a window toolkit that comes *built into* Python, so there is
nothing to install.

The smallest possible window:

```python
import tkinter as tk

root = tk.Tk()                      # the main window
root.title("My App")
root.geometry("400x300")            # width x height

label = tk.Label(root, text="Hello")
label.pack()                        # place it in the window

button = tk.Button(root, text="Click me",
                   command=lambda: print("clicked"))
button.pack()

root.mainloop()                     # keep the window open
```

Run it and a real window appears.

## 12.1 The parts explained

- `tk.Tk()` creates the window.
- `tk.Label`, `tk.Button`, `tk.Entry` (a text box) are called **widgets**.
- `.pack()` puts a widget into the window. (`.grid()` places things in a table
  instead — the real app mixes both.)
- `command=...` is the function to run when the button is clicked.
- `lambda: print("clicked")` is a tiny throwaway function. You need it whenever
  you just want "do this little thing" without a full `def`.
- `root.mainloop()` starts the window listening for clicks. **Everything before
  mainloop sets up the window; mainloop is what actually shows it.**

## 12.2 Tabs

A tabbed window is a `Notebook`:

```python
from tkinter import ttk

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

tab1 = ttk.Frame(notebook, padding=20)
notebook.add(tab1, text="Folders")

tab2 = ttk.Frame(notebook, padding=20)
notebook.add(tab2, text="Run")
```

Each tab is a `Frame` (a container) that you then put widgets into.

## 12.3 Reading a text box

```python
text_var = tk.StringVar()               # a value the window watches
entry = tk.Entry(root, textvariable=text_var)
entry.pack()

# later, when a button is clicked:
chosen = text_var.get()                 # read what the user typed
text_var.set("new text")                # put text in
```

`StringVar` is a "variable" that belongs to the window, so widgets can show it
and keep it updated automatically.

## 12.4 The button that actually runs the app

The window does not re-implement anything. It **calls the same functions the
command line uses**:

```python
def organize_clicked():
    moves, skipped = plan(source_folder, settings)   # from organizer.py
    apply_moves(moves, settings)

ttk.Button(tab2, text="Organize now", command=organize_clicked).pack()
```

> **The lesson of this whole stage:** separate "the thinking" (organizer.py)
> from "the buttons" (gui.py). One brain, two mouths. If you ever want a web
> version too, you add another mouth — you never touch the brain. That is why
> the project is split into several small files instead of one giant one.

Open `gui.py` and read it with these ideas in mind. It is long, but you will now
recognise every piece: tabs, labels, buttons, text boxes, and calls into
`organizer.py` and `history.py`.

One detail worth knowing: the **Run** tab does its work on a *background thread*
so the window does not freeze while it scans. A thread is like a second worker
doing a job while the main one keeps the window responsive. Look for
`threading.Thread(...)` in `gui.py`. You do not need to master threads yet —
just know that is what it is for.

### 12.5 The finished window's shape

`gui.py` is one big `class App`. A **class** is a bundle of data and functions
that belong together — here, "the window and everything it can do". You create
it once with `App(root)`, and `__init__` builds everything:

```python
class App:
    def __init__(self, root):
        self.root = root          # self.* is the class's own memory
        self.cfg = config.load()  # settings, loaded once
        self.watching = False
        self._build_header()
        self._build_tabs()        # creates the four tabs
        self._refresh_all()       # fills the boxes with saved values
```

`self` is how a class refers to itself. `self.cfg` means "my cfg". Whenever you
see `self.` in `gui.py`, the window is remembering something.

The four tabs are made by four functions — `_tab_folders`, `_tab_categories`,
`_tab_patterns`, `_tab_run` — each creating its own widgets. The leading `_` is
just a convention meaning "internal helper".

### 12.6 Tables, lists and number boxes

Three more widgets the finished app uses:

**A table** for the pattern list is a `Treeview`:

```python
tree = ttk.Treeview(tab, columns=("count", "signal"), show="headings")
tree.heading("count", text="Files")
tree.column("count", width=60)
tree.insert("", "end", values=(8, "inner:factorio-mod"))
```

**A plain list** (for the accepted rules) is a `Listbox`:

```python
box = tk.Listbox(tab)
box.insert("end", "inner:factorio-mod  ->  Factorio Mods")
selected = box.curselection()      # which line is highlighted
```

**A number box with little up/down arrows** is a `Spinbox`:

```python
tk.Spinbox(row, from_=0, to=300, textvariable=age_var, width=6)
```

Finding the highlighted row back is how the **Accept selected pattern** and
**Remove selected rule** buttons know what you clicked.

### 12.7 Running slow work without freezing the window

Scanning a big folder takes a few seconds. If you did it inside the click
function, the window would freeze solid until it finished. So the finished app
runs the work on a **thread** and hands the result back afterwards:

```python
def find_patterns(self):
    def work():                              # runs on the background thread
        files, _ = organizer.read_folder(source, self.cfg)
        found = patterns.suggest(files, self.cfg)
        self.root.after(0, lambda: self._show_patterns(found))   # back to the UI

    threading.Thread(target=work, daemon=True).start()
```

Two things make this safe:

- `threading.Thread(target=work).start()` runs `work` in the background.
  `daemon=True` means the thread dies if you close the window.
- `self.root.after(0, ...)` means "when convenient, run this back on the main
  window thread". **Never touch widgets from a background thread** — that is the
  one rule of threads, and `after` is the safe handover.

That is exactly what `find_patterns()`, `run()` and `_watch_loop()` do in
`gui.py`, and why the window stays clickable while it scans.

---

# Part 13 — Stage 12: turning it into a Windows .exe

Right now you run the app with `python gui.py`. That needs Python installed.
An **.exe** is a single file anyone can double-click. We use **PyInstaller**.

## 13.1 Install it

```powershell
python -m pip install pyinstaller
```

`pip` is Python's app store. `-m pip` means "run the pip module".

## 13.2 Build

In the project folder:

```powershell
python -m PyInstaller --onefile --windowed --name DownloadOrganizer run.py
```

The options:

- `--onefile` — pack everything into a single `.exe`.
- `--windowed` — no black console window behind the app (right for a GUI).
- `--name DownloadOrganizer` — what the file will be called.
- `run.py` — the entry point; it just opens the window.

After a minute or two you get:

```
dist/DownloadOrganizer.exe     <-- this is your app
```

Double-click it. It opens like any Windows program. Copy it anywhere, or give it
to a friend — that one file is the whole thing.

## 13.3 What PyInstaller actually does

It looks at your code, finds every tool it uses (our imports, plus a copy of
Python itself), and glues them all into one big file. That is why the `.exe` is
about 13 MB — it is carrying Python around with it.

> **A warning about antivirus and SmartScreen.** Windows sometimes shows "unknown
> publisher" for a new `.exe`, because nobody paid for a signing certificate.
> That is normal for homemade apps. Click "More info" → "Run anyway".

## 13.4 Why settings move to %APPDATA%

When `run.py` is packed into an `.exe`, there is no source folder on disk to
save `config.json` into. So the app saves your settings to
`%APPDATA%\DownloadOrganizer` instead. In Explorer you can paste
`%APPDATA%\DownloadOrganizer` into the address bar to see it. This is how
normal Windows apps behave, and `config.py` checks for it with:

```python
if getattr(sys, "frozen", False):     # "frozen" = running as a built exe
    ...use %APPDATA%...
```

---

# Part 14 — Git and GitHub, explained properly

This trips up every beginner, so let us go slowly. Two different things, often
confused:

- **Git** — a program on your computer that saves versions of your work. Like an
  unlimited "save game" history you can jump back to.
- **GitHub** — a website that stores a copy of your Git projects online, so you
  can back them up, share them, and show them to employers.

Git = the tool. GitHub = the place. You can use Git without GitHub.

## 14.1 Why bother?

- A safety net: made a mess? Go back to how it was an hour ago.
- A portfolio: employers look at GitHub. "Here is code I wrote and understand"
  beats an empty CV.
- Backup: your laptop dies, your code is safe online.

## 14.2 Install Git

Download from <https://git-scm.com/download/win>. Install with the defaults.
Check it:

```powershell
git --version
```

## 14.3 Tell Git who you are (once)

```powershell
git config --global user.name "Muneeb Khan"
git config --global user.email "you@example.com"
```

Use the same email you will use on GitHub. This name gets attached to every
"save" you make.

## 14.4 The three-step idea: working → staged → saved

Git thinks in three places:

1. **Working folder** — the actual files you edit.
2. **Staging area** — files you have picked to include in the next save.
3. **Repository / commit history** — your saved snapshots.

A **commit** is one snapshot, with a message describing what changed.

## 14.5 Start tracking your project

In your project folder:

```powershell
git init
```

This creates a hidden `.git` folder — that is Git's memory. Do not delete it.

Now add a `.gitignore` file. It lists things Git should **not** save (junk you
do not want online):

```
__pycache__/
build/
config.json
history.json
demo_downloads/
```

> **Why ignore `config.json`?** It holds *your* personal settings and folder
> paths. `__pycache__` and `build/` are generated junk that rebuilds itself. You
> never commit those.

## 14.6 Save your first snapshot

```powershell
git add .
git commit -m "First version of the download organizer"
```

- `git add .` stages everything in the folder (the `.` means "here").
- `git commit -m "message"` saves the snapshot with that message. Write messages
  that describe *what changed*, e.g. `"Add undo support"`.

Check the state any time:

```powershell
git status      # what has changed since the last save
git log --oneline   # the list of your commits
```

## 14.7 Put it on GitHub

1. Make a free account at <https://github.com>.
2. Click **New repository**. Name it `download-organizer`. **Do not** add a
   README or .gitignore — you already have those. Click Create.
3. GitHub shows you a URL like `https://github.com/yourname/download-organizer.git`.
4. Connect your local project to it and push:

```powershell
git remote add origin https://github.com/yourname/download-organizer.git
git branch -M main
git push -u origin main
```

- `git remote add origin <url>` tells Git where the online copy lives. `origin`
  is just a nickname for that URL.
- `git branch -M main` renames your branch to `main` (GitHub's default name).
- `git push -u origin main` uploads your commits. `-u` remembers the pairing, so
  after this you can just type `git push`.

Refresh the GitHub page. Your files are there. That is your first repo.

## 14.8 The everyday rhythm

After the first setup, the loop is always the same three commands:

```powershell
git add .
git commit -m "Describe what you changed"
git push
```

Do this every time you finish a chunk of work. Small, frequent commits are
better than one giant one.

## 14.9 Logging in / tokens

GitHub no longer accepts your normal password for `git push`. When it asks, you
need a **Personal Access Token**:

1. On GitHub: your picture → Settings → Developer settings → Personal access
   tokens → Tokens (classic) → Generate new token.
2. Give it a name, tick **repo**, generate, and **copy the token**.
3. When Git asks for a password, paste the token instead.

Save it once and Git remembers it. (An alternative is an SSH key, which is
neater but a longer setup — the token route is fine to start.)

## 14.10 Two bonus Git skills

**Cloning** means downloading someone else's project:

```powershell
git clone https://github.com/someone/their-project.git
```

**Undoing a bad change** — if you edited files and want them back as they were
at your last commit:

```powershell
git restore .
```

Careful: that throws away your uncommitted edits. It is your safety net, but it
is a one-way door for anything you never committed.

> **Plain-English summary.** Git saves snapshots of your folder locally.
> `git add .` picks what to include, `git commit -m "..."` saves the snapshot,
> `git push` uploads it to GitHub. That is 90% of daily Git.

---

# Part 15 — When things go wrong

**`python is not recognized`**
Python is not on your PATH. Re-run the installer and tick "Add python.exe to
PATH".

**`ModuleNotFoundError: No module named 'tkinter'`**
Rare on Windows. Re-run the Python installer and make sure "tcl/tk and IDLE" is
ticked.

**`PermissionError` when moving a file**
The file is open in another program (or still downloading). Close it and retry.
The app also skips recently-changed files for this reason.

**A file went to the wrong folder**
That is not a bug — it is feedback. Add or fix a rule in the Patterns tab, or
add the missing extension to the right category. The app is meant to be taught.

**The .exe shows "Windows protected your PC"**
Normal for unsigned homemade programs. "More info" → "Run anyway".

**`fatal: not a git repository`**
You are running Git in the wrong folder. `cd` into your project folder first.

**I messed up my files**
Run the Undo button (or `python organizer.py --undo`). And in future: always
`--dry-run` first.

---

## You built it

Take a second to notice what you now know:

- Reading a file's **bytes** to identify its real type.
- Reading its **text** to guess what kind of text it is.
- Turning measurements into **signals**, and signals into **patterns**.
- Letting a *user* confirm a pattern, and remembering it as a **rule**.
- Guarding against half-finished and duplicate files.
- The difference between a **dry run** and a real run.
- Two front ends — command line and window — over one **engine**.
- Packaging a Python program into a Windows **.exe**.
- Saving versions of your work with **Git**, and publishing with **GitHub**.

That is a real chunk of practical programming. The specific app matters less than
the habits: **build the smallest thing that works, add one idea at a time, and
prove each step before moving on.**

---

# Part 16 — The complete file map (answer key)

You built the app. Here is where each idea ended up, and what the finished code
calls it. Search the real files for these names whenever you lose your way.

| You built (tutorial) | Finished file | What it is |
|---|---|---|
| `EXTENSIONS` dict | `categories` in `config.py` | extension -> folder |
| `sort_folder()` | `plan()` + `apply_moves()` | decide, then move |
| `sniff_type()` | `magic_type()` in `patterns.py` | bytes -> real file type |
| `sniff_text()` | `_looks_like_text()` in `patterns.py` | is this text at all? |
| `analyze()` | `analyze()` in `patterns.py` | all signals for one file |
| `suggest()` | `suggest()` in `patterns.py` | count signals, propose folders |
| `friendly_name()` | `friendly_folder()` + `FRIENDLY_FOLDERS` | signal -> nice name |
| `PARTIAL` set + age check | `looks_like_download()` | skip half-done files |
| `free_name()` | `unique_destination()` | never overwrite |
| reading the folder | `read_folder()` | walk + analyse |
| `load_settings()` / `save_settings()` | `config.load()` / `config.save()` | settings |
| `remember()` / `undo_last()` | `history.record()` / `history.undo_last()` | undo |
| the window | `class App` in `gui.py` | the four tabs |
| building the exe | `run.py` + PyInstaller | the `.exe` |

Two files the tutorial did not walk through line by line, worth a read now that
you understand the ideas:

- **`config.py`** — mostly the `DEFAULTS` dictionary and a `data_dir()` that
  switches between the project folder and `%APPDATA%` when running as an `.exe`.
- **`make_demo_files.py`** — builds `demo_downloads/`. It is short, and handy to
  copy when you want your own test files.

A handful of small plumbing helpers are worth knowing by name, since you will
pass them every time you read the code:

| Helper | Where | Job |
|---|---|---|
| `config_path()` / `history_path()` | `config.py`, `history.py` | where those files live |
| `build_extension_lookup()` | `organizer.py` | flips `{folder: [exts]}` into `{ext: folder}` |
| `resolve_source()` / `resolve_target()` | `organizer.py` | turn settings into real paths |
| `_print_moves()` | `organizer.py` | the tidy grouped printout you see in the terminal |
| `cleanup_empty_folders()` | `organizer.py` | removes empty category folders after a real run |

The tutorial deliberately uses simpler names than the finished code (a student
version). That is normal — real projects get renamed and reorganised as they
grow. What matters is that you can now open the real files and recognise every
idea in them. That was the point of the whole exercise.
