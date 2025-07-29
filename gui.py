import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import datetime
import os
from network_monitor import NetworkMonitor

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, monitor_vars):
        super().__init__(parent)
        self.title("Settings")
        self.resizable(False, False)
        self.monitor_vars = monitor_vars
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH)

        ttk.Checkbutton(
            frm, text="Remove Stale",
            variable=monitor_vars['remove_stale']
        ).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(
            frm, text="Verbose",
            variable=monitor_vars['verbose']
        ).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(frm, text="Interval (s):").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(
            frm, width=6,
            textvariable=monitor_vars['interval']
        ).grid(row=2, column=1)
        ttk.Label(frm, text="JSON File:").grid(row=3, column=0, sticky=tk.W)
        path_entry = ttk.Entry(
            frm, width=40,
            textvariable=monitor_vars['json_path']
        )
        path_entry.grid(row=3, column=1)
        ttk.Button(
            frm, text="Browse...",
            command=lambda: self.browse_json(path_entry)
        ).grid(row=3, column=2)
        ttk.Button(
            frm, text="Close", command=self.destroy
        ).grid(row=4, column=1, pady=10)

    def browse_json(self, entry):
        p = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files","*.json")],
            initialfile=entry.get()
        )
        if p:
            self.monitor_vars['json_path'].set(p)

class NetworkMonitorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Network Monitor GUI")
        self.geometry("900x600")
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Treeview', rowheight=24)
        cols = ("mac","ip","first_seen","last_seen")
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        for c,w in zip(cols,(180,120,200,200)):
            self.tree.heading(c,text=c.title())
            self.tree.column(c,width=w)
        self.tree.pack(fill=tk.BOTH, expand=True)
        ctrl = ttk.Frame(self, padding=10)
        ctrl.pack(fill=tk.X)
        self.vars = {
            'remove_stale': tk.BooleanVar(value=False),
            'verbose'   : tk.BooleanVar(value=False),
            'interval'  : tk.IntVar(value=30),
            'json_path' : tk.StringVar(value='devices.json')
        }
        ttk.Button(ctrl, text="Start", command=self.start).pack(side=tk.LEFT)
        ttk.Button(ctrl, text="Stop", command=self.stop, state=tk.DISABLED).pack(side=tk.LEFT)
        ttk.Button(ctrl, text="Settings", command=self.open_settings).pack(side=tk.RIGHT)
        self.monitor = NetworkMonitor()
        self._running = False

    def open_settings(self):
        SettingsDialog(self, self.vars)

    def start(self):
        self.monitor.remove_stale = self.vars['remove_stale'].get()
        self.monitor.verbose = self.vars['verbose'].get()
        self.interval = self.vars['interval'].get()
        self.json_path = self.vars['json_path'].get()
        if os.path.exists(self.json_path): os.remove(self.json_path)
        for btn in self.children['!frame'].winfo_children():
            if btn.cget('text')=='Start': btn.state(['disabled'])
            if btn.cget('text')=='Stop':  btn.state(['!disabled'])
        self._running = True
        self._schedule()

    def stop(self):
        self._running = False
        for btn in self.children['!frame'].winfo_children():
            if btn.cget('text')=='Start': btn.state(['!disabled'])
            if btn.cget('text')=='Stop':  btn.state(['disabled'])

    def _schedule(self):
        if not self._running: return
        threading.Thread(target=self._scan, daemon=True).start()
        self.after(self.vars['interval'].get()*1000, self._schedule)

    def _scan(self):
        try:
            self.monitor.scan()
            self.monitor.to_json(self.vars['json_path'].get())
            self._refresh(self.monitor.devices())
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def _refresh(self, devices):
        for iid in self.tree.get_children(): self.tree.delete(iid)
        for idx, d in enumerate(sorted(devices, key=lambda x: x.ip_address)):
            tag = 'even' if idx % 2 == 0 else 'odd'
            f = datetime.datetime.fromisoformat(d.date_added).strftime('%Y-%m-%d %H:%M:%S')
            l = datetime.datetime.fromisoformat(d.last_seen).strftime('%Y-%m-%d %H:%M:%S')
            self.tree.insert('', tk.END, values=(d.mac_address, d.ip_address, f, l), tags=(tag,))

if __name__ == '__main__':
    NetworkMonitorGUI().mainloop()