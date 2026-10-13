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

    # -- prettiness -------------------------------------------------------
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

    def _build_header(self):
        bar = tk.Frame(self.root, bg=CARD, height=58)
        bar.pack(fill="x")
        tk.Label(bar, text="  Download Organizer", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left", pady=14)
        self.status = tk.Label(bar, text="", bg=CARD, fg=MUTED,
                               font=("Segoe UI", 9))
        self.status.pack(side="right", padx=16)

    def _build_tabs(self):
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=12, pady=12)
        self._tab_folders(nb)
        self._tab_categories(nb)
        self._tab_patterns(nb)
        self._tab_run(nb)

    # -- tab: folders -----------------------------------------------------
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

    # -- tab: categories --------------------------------------------------
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

    # -- tab: patterns ----------------------------------------------------
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

    # -- tab: run ---------------------------------------------------------
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

    def _log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

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

    def undo(self):
        restored, problems = history.undo_last()
        self._log(f"\n=== UNDO === restored {restored} file(s)")
        for problem in problems:
            self._log(f"  - {problem}")
        self._set_status("undone")

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

    # -- shared -----------------------------------------------------------
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


def main():
    config.save(config.load())        # make sure config.json exists
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
