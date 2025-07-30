import datetime
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Literal

from network_monitor import NetworkMonitor


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, monitor_vars: dict[str, tk.Variable]) -> None:
        super().__init__(parent)
        self.title("Settings")
        self.resizable(False, False)
        self.monitor_vars = monitor_vars

        frm = ttk.Frame(self, padding=10)
        # use literal strings for **fill** to match stub‑types
        frm.pack(fill="both", expand=True)

        ttk.Checkbutton(
            frm, text="Remove Stale", variable=monitor_vars["remove_stale"]
        ).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(
            frm, text="Verbose", variable=monitor_vars["verbose"]
        ).grid(row=1, column=0, sticky="w")

        ttk.Label(frm, text="Interval (s):").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm, width=6, textvariable=monitor_vars["interval"]).grid(
            row=2, column=1
        )

        ttk.Label(frm, text="JSON File:").grid(row=3, column=0, sticky="w")
        path_entry = ttk.Entry(frm, width=40, textvariable=monitor_vars["json_path"])
        path_entry.grid(row=3, column=1)
        ttk.Button(
            frm, text="Browse…", command=lambda: self._browse_json(path_entry)
        ).grid(row=3, column=2)

        ttk.Button(frm, text="Close", command=self.destroy).grid(
            row=4, column=1, pady=10
        )

    # --------------------------------------------------------------------- #
    # helpers
    # --------------------------------------------------------------------- #
    def _browse_json(self, entry: ttk.Entry) -> None:
        p = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=entry.get(),
        )
        if p:
            self.monitor_vars["json_path"].set(p)


class NetworkMonitorGUI(tk.Tk):
    # ----------------------------------------------------------------- #
    # construction
    # ----------------------------------------------------------------- #
    def __init__(self) -> None:
        super().__init__()
        self.title("Network Monitor GUI")
        self.geometry("900x600")

        # silence “attribute defined outside __init__” warnings
        self.interval: int | None = None
        self.json_path: str | None = None

        # ---------------------------------------------------------------- #
        # widgets
        # ---------------------------------------------------------------- #
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=24)

        cols: tuple[str, ...] = ("mac", "ip", "first_seen", "last_seen")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")

        for c, w in zip(cols, (180, 120, 200, 200), strict=False):
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=w)

        self.tree.pack(fill="both", expand=True)

        ctrl = ttk.Frame(self, padding=10)
        ctrl.pack(fill="x")

        # control variables
        self.vars: dict[str, tk.Variable] = {
            "remove_stale": tk.BooleanVar(value=False),
            "verbose": tk.BooleanVar(value=False),
            "interval": tk.IntVar(value=30),
            "json_path": tk.StringVar(value="devices.json"),
        }

        ttk.Button(ctrl, text="Start", command=self.start).pack(side="left")
        ttk.Button(ctrl, text="Stop", command=self.stop, state=tk.DISABLED).pack(
            side="left"
        )
        ttk.Button(ctrl, text="Settings", command=self.open_settings).pack(side="right")

        self.monitor = NetworkMonitor()
        self._running = False

    # ----------------------------------------------------------------- #
    # public handlers
    # ----------------------------------------------------------------- #
    def open_settings(self) -> None:
        SettingsDialog(self, self.vars)

    def start(self) -> None:
        # propagate GUI settings into the monitor
        self.monitor.remove_stale = bool(self.vars["remove_stale"].get())
        self.monitor.verbose = bool(self.vars["verbose"].get())

        # cache for convenience / pylint
        self.interval = int(self.vars["interval"].get())
        self.json_path = str(self.vars["json_path"].get())

        # fresh JSON each run
        if os.path.exists(self.json_path):
            os.remove(self.json_path)

        # enable / disable buttons
        for btn in self.children["!frame"].winfo_children():  # type: ignore[index]
            if btn.cget("text") == "Start":
                btn.state(["disabled"])
            if btn.cget("text") == "Stop":
                btn.state(["!disabled"])

        self._running = True
        self._schedule()

    def stop(self) -> None:
        self._running = False
        for btn in self.children["!frame"].winfo_children():  # type: ignore[index]
            if btn.cget("text") == "Start":
                btn.state(["!disabled"])
            if btn.cget("text") == "Stop":
                btn.state(["disabled"])

    # ----------------------------------------------------------------- #
    # internals
    # ----------------------------------------------------------------- #
    def _schedule(self) -> None:
        if not self._running:
            return
        threading.Thread(target=self._scan, daemon=True).start()
        self.after(self.interval * 1000, self._schedule)  # type: ignore[arg-type]

    def _scan(self) -> None:
        try:
            self.monitor.scan()
            self.monitor.to_json(self.json_path)
            self._refresh(self.monitor.devices())
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Error", str(exc))

    def _refresh(self, devices) -> None:  # type: ignore[override]
        # clear existing rows
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        # repopulate
        for idx, device in enumerate(sorted(devices, key=lambda x: x.ip_address)):
            tag = "even" if idx % 2 == 0 else "odd"
            first = datetime.datetime.fromisoformat(device.date_added).strftime(
                "%Y‑%m‑%d %H:%M:%S"
            )
            last = datetime.datetime.fromisoformat(device.last_seen).strftime(
                "%Y‑%m‑%d %H:%M:%S"
            )
            self.tree.insert(
                "",  # parent
                "end",  # index
                values=(device.mac_address, device.ip_address, first, last),
                tags=(tag,),
            )


if __name__ == "__main__":
    NetworkMonitorGUI().mainloop()