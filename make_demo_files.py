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
