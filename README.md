# Download Organizer

A Windows app that tidies your Downloads folder. It sorts files into category
folders, and it does **not** just trust the file name — it opens each file and
looks at what is really inside.

The clever part is the **pattern engine**: when several downloads share an
unusual trait (all Factorio mods, all screenshots, all Android apps), the app
notices the pattern and suggests giving them their own folder. You accept the
suggestion once and it files them there from then on. Nothing about Minecraft
or any other game is hard-coded — it learns the patterns in *your* downloads.

## Two ways to use it

### The app (easiest)

Run `DownloadOrganizer.exe` from the `dist` folder. Or, from source:

```bash
python gui.py
```

A window opens with four tabs:

- **Folders** — which folder to watch, where to sort into.
- **Categories** — edit the extension lists per folder.
- **Patterns** — find patterns and accept them as rules.
- **Run** — Scan (preview), Organize, Undo, and Start watching.

### The command line

```bash
python organizer.py                  # sort Downloads once
python organizer.py --dry-run        # preview, change nothing
python organizer.py --watch 30       # re-scan every 30 seconds
python organizer.py --suggest        # list patterns it has noticed
python organizer.py --accept inner:factorio-mod --folder "Factorio Mods"
python organizer.py --undo           # put back the last run
```

## How it decides where a file goes

Checked in order, first match wins:

1. **Rules you accepted** from the Patterns tab — always win.
2. **Automatic signals** — things that are obviously their own folder
   (screenshots by name, Android apps by contents, Minecraft mods, …).
3. **The file's real type**, read from its first bytes (magic bytes). A PNG
   saved as `.txt` still goes to Images.
4. **The extension**, from `config.json`.

Inside archives it looks for tell-tale files: `fabric.mod.json`, `pack.mcmeta`,
`AndroidManifest.xml`, `info.json`, `About/About.xml`, `package.json`,
`Dockerfile`, and more. Each recognised trait is a *signal*.

## What it can detect out of the box

- **Real file types** from bytes: images, video, audio, fonts, 3D models,
  documents, executables, archives.
- **Inside archives**: Minecraft mods/packs/shaders, Android apps, Word/Excel/
  PowerPoint files, EPUBs, Node projects, Java libraries, modpacks, web pages,
  Factorio mods, RimWorld mods, Docker projects.
- **From the name**: screenshots, WhatsApp files, invoices, receipts, phone
  photos (`IMG_`), camera photos (`DSC_`), and more.
- **Version numbers** in names become subfolders, e.g.
  `Minecraft Mods/1.20.1/`.

Adding a new pattern is mostly *data*, not code — add a line to
`FRIENDLY_FOLDERS` in `patterns.py` and it gets a proper name.

## Safety

- **Scan** previews; **Organize** moves. Always scan first.
- **Undo** puts back the last run (history is kept for the last 20 runs).
- Skips `.part` / `.crdownload` / `.tmp` and files changed in the last few
  seconds, so half-finished downloads are left alone.
- Never overwrites — duplicates become `name (1).ext`.
- Everything is local. Nothing is uploaded anywhere.

## Building the .exe yourself

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name DownloadOrganizer run.py
```

The result lands in `dist/DownloadOrganizer.exe`. That single file is the whole
app — you can copy it anywhere.

When running as an .exe, your settings live in
`%APPDATA%\DownloadOrganizer\` instead of the project folder, so the app works
from any location.

## Project files

```
download-organizer/
├── organizer.py        # the engine: classify + move + undo hooks
├── patterns.py         # the pattern engine: signals and suggestions
├── config.py           # settings, and where files are stored
├── history.py          # the undo history
├── gui.py              # the desktop window (tkinter)
├── run.py              # entry point for the .exe
├── make_demo_files.py  # builds a safe fake Downloads folder
├── BUILD-ALONG.md      # build the REAL app yourself, file by file (start here)
├── TUTORIAL.md         # the ideas explained by building mini-versions
├── README.md
└── dist/
    └── DownloadOrganizer.exe
```

## Try it safely

```bash
python make_demo_files.py            # makes demo_downloads/
python organizer.py demo_downloads --dry-run
python organizer.py demo_downloads --suggest
```

`demo_downloads/` is a fake folder, so you can experiment without touching your
real Downloads.
