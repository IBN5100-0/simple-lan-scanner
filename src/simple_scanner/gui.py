"""Modern GUI implementation for LAN Scanner with improved UX."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime
import threading
from typing import Optional, Dict, Any
import os
import json
from pathlib import Path

from .scanner import NetworkMonitor, autodetect_network, get_user_data_dir
from .models import Device


class ModernSettingsDialog(tk.Toplevel):
    """Modern settings dialog with tabs and better organization."""
    
    def __init__(self, parent: tk.Tk, settings: Dict[str, Any]) -> None:
        super().__init__(parent)
        self.title("Settings")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Configure window background
        self.configure(bg='#f0f0f0')
        
        # Center the dialog
        self.transient(parent)
        self.grab_set()
        
        # Center on parent window
        self.update_idletasks()
        x = (parent.winfo_x() + (parent.winfo_width() // 2) - (600 // 2))
        y = (parent.winfo_y() + (parent.winfo_height() // 2) - (500 // 2))
        self.geometry(f"+{x}+{y}")
        
        self.settings = settings
        self.temp_settings = settings.copy()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self, padding=10)
        notebook.pack(fill="both", expand=True)
        
        # Scan Settings Tab
        scan_frame = ttk.Frame(notebook, padding=20)
        notebook.add(scan_frame, text="Scan Settings")
        self._create_scan_settings(scan_frame)
        
        # Network Settings Tab
        network_frame = ttk.Frame(notebook, padding=20)
        notebook.add(network_frame, text="Network")
        self._create_network_settings(network_frame)
        
        # Output Settings Tab
        output_frame = ttk.Frame(notebook, padding=20)
        notebook.add(output_frame, text="Output")
        self._create_output_settings(output_frame)
        
        # Advanced Tab
        advanced_frame = ttk.Frame(notebook, padding=20)
        notebook.add(advanced_frame, text="Advanced")
        self._create_advanced_settings(advanced_frame)
        
        # Buttons with proper sizing
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", side="bottom", pady=10)
        
        # Style configuration for buttons with explicit colors
        style = ttk.Style()
        style.configure(
            "Dialog.TButton", 
            padding=(10, 5),
            relief="raised",
            borderwidth=2
        )
        
        # Create buttons with explicit styling
        cancel_btn = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.destroy, 
            width=12,
            style="Dialog.TButton"
        )
        cancel_btn.pack(side="right", padx=(5, 10), pady=5)
        
        apply_btn = ttk.Button(
            button_frame, 
            text="Apply", 
            command=self._apply_settings, 
            width=12,
            style="Dialog.TButton"
        )
        apply_btn.pack(side="right", padx=5, pady=5)
        
        ok_btn = ttk.Button(
            button_frame, 
            text="OK", 
            command=self._ok_settings, 
            width=12,
            style="Dialog.TButton"
        )
        ok_btn.pack(side="right", padx=(10, 5), pady=5)
        
    def _create_scan_settings(self, parent: ttk.Frame) -> None:
        """Create scan settings controls."""
        # Title
        title = ttk.Label(parent, text="Scan Configuration", font=("", 12, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # Scan interval
        ttk.Label(parent, text="Scan Interval:").grid(row=1, column=0, sticky="w", pady=5)
        interval_frame = ttk.Frame(parent)
        interval_frame.grid(row=1, column=1, sticky="w", pady=5)
        
        self.interval_var = tk.IntVar(value=self.temp_settings.get("interval", 30))
        interval_spin = ttk.Spinbox(interval_frame, from_=5, to=3600, textvariable=self.interval_var, width=10)
        interval_spin.pack(side="left")
        ttk.Label(interval_frame, text="seconds").pack(side="left", padx=5)
        
        # Auto-start
        self.autostart_var = tk.BooleanVar(value=self.temp_settings.get("autostart", False))
        ttk.Checkbutton(parent, text="Start scanning automatically on launch", 
                       variable=self.autostart_var).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        
        # Remove stale devices
        self.remove_stale_var = tk.BooleanVar(value=self.temp_settings.get("remove_stale", False))
        ttk.Checkbutton(parent, text="Remove devices not seen in last scan", 
                       variable=self.remove_stale_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        
        # Notification settings
        notif_frame = ttk.LabelFrame(parent, text="Notifications", padding=10)
        notif_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=20)
        
        self.notify_new_var = tk.BooleanVar(value=self.temp_settings.get("notify_new", True))
        ttk.Checkbutton(notif_frame, text="Notify when new device found", 
                       variable=self.notify_new_var).pack(anchor="w", pady=2)
        
        self.notify_change_var = tk.BooleanVar(value=self.temp_settings.get("notify_change", False))
        ttk.Checkbutton(notif_frame, text="Notify when device IP changes", 
                       variable=self.notify_change_var).pack(anchor="w", pady=2)
        
    def _create_network_settings(self, parent: ttk.Frame) -> None:
        """Create network settings controls."""
        # Title
        title = ttk.Label(parent, text="Network Configuration", font=("", 12, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")
        
        # Network selection
        ttk.Label(parent, text="Network to scan:").grid(row=1, column=0, sticky="w", pady=5)
        
        self.network_var = tk.StringVar(value=self.temp_settings.get("network", "auto"))
        self.network_combo = ttk.Combobox(parent, textvariable=self.network_var, width=20)
        self.network_combo.grid(row=1, column=1, sticky="w", pady=5)
        
        # Detect networks button
        ttk.Button(parent, text="Detect", command=self._detect_networks).grid(row=1, column=2, padx=5)
        
        # Auto-detect radio
        self.network_mode = tk.StringVar(value="auto" if self.network_var.get() == "auto" else "manual")
        ttk.Radiobutton(parent, text="Auto-detect network", variable=self.network_mode, 
                       value="auto", command=self._update_network_mode).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Radiobutton(parent, text="Manual network selection", variable=self.network_mode, 
                       value="manual", command=self._update_network_mode).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        
        # Timeout settings
        timeout_frame = ttk.LabelFrame(parent, text="Timeout Settings", padding=10)
        timeout_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=20)
        
        ttk.Label(timeout_frame, text="Scan timeout:").grid(row=0, column=0, sticky="w", pady=5)
        self.timeout_var = tk.IntVar(value=self.temp_settings.get("timeout", 300))
        timeout_spin = ttk.Spinbox(timeout_frame, from_=30, to=600, textvariable=self.timeout_var, width=10)
        timeout_spin.grid(row=0, column=1, sticky="w", pady=5)
        ttk.Label(timeout_frame, text="seconds").grid(row=0, column=2, sticky="w", padx=5)
        
    def _create_output_settings(self, parent: ttk.Frame) -> None:
        """Create output settings controls."""
        # Title
        title = ttk.Label(parent, text="Output Configuration", font=("", 12, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")
        
        # File outputs
        output_frame = ttk.LabelFrame(parent, text="File Outputs", padding=10)
        output_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=10)
        
        # JSON output
        self.json_enabled_var = tk.BooleanVar(value=bool(self.temp_settings.get("json_path", "")))
        json_check = ttk.Checkbutton(output_frame, text="Save to JSON file:", 
                                     variable=self.json_enabled_var, command=self._toggle_json)
        json_check.grid(row=0, column=0, sticky="w", pady=5)
        
        self.json_path_var = tk.StringVar(value=self.temp_settings.get("json_path", ""))
        self.json_entry = ttk.Entry(output_frame, textvariable=self.json_path_var, width=40)
        self.json_entry.grid(row=0, column=1, pady=5, padx=5)
        
        self.json_browse_btn = ttk.Button(output_frame, text="Browse...", 
                                         command=lambda: self._browse_file(self.json_path_var, "JSON", "*.json"))
        self.json_browse_btn.grid(row=0, column=2, pady=5)
        
        # CSV output
        self.csv_enabled_var = tk.BooleanVar(value=bool(self.temp_settings.get("csv_path", "")))
        csv_check = ttk.Checkbutton(output_frame, text="Save to CSV file:", 
                                    variable=self.csv_enabled_var, command=self._toggle_csv)
        csv_check.grid(row=1, column=0, sticky="w", pady=5)
        
        self.csv_path_var = tk.StringVar(value=self.temp_settings.get("csv_path", ""))
        self.csv_entry = ttk.Entry(output_frame, textvariable=self.csv_path_var, width=40)
        self.csv_entry.grid(row=1, column=1, pady=5, padx=5)
        
        self.csv_browse_btn = ttk.Button(output_frame, text="Browse...", 
                                        command=lambda: self._browse_file(self.csv_path_var, "CSV", "*.csv"))
        self.csv_browse_btn.grid(row=1, column=2, pady=5)
        
        # Timestamp options
        self.timestamp_var = tk.BooleanVar(value=self.temp_settings.get("timestamp_files", False))
        ttk.Checkbutton(output_frame, text="Add timestamp to filenames", 
                       variable=self.timestamp_var).grid(row=2, column=0, columnspan=3, sticky="w", pady=5)
        
        # Update controls state
        self._toggle_json()
        self._toggle_csv()
        
    def _create_advanced_settings(self, parent: ttk.Frame) -> None:
        """Create advanced settings controls."""
        # Title
        title = ttk.Label(parent, text="Advanced Settings", font=("", 12, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # Verbose mode
        self.verbose_var = tk.BooleanVar(value=self.temp_settings.get("verbose", False))
        ttk.Checkbutton(parent, text="Verbose mode (show detailed output)", 
                       variable=self.verbose_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        # MAC lookup
        self.mac_lookup_var = tk.BooleanVar(value=self.temp_settings.get("mac_lookup", True))
        ttk.Checkbutton(parent, text="Enable MAC address vendor lookup", 
                       variable=self.mac_lookup_var).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        
        # Persistence
        persist_frame = ttk.LabelFrame(parent, text="Data Persistence", padding=10)
        persist_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=20)
        
        self.persist_var = tk.BooleanVar(value=self.temp_settings.get("use_persistence", True))
        ttk.Checkbutton(persist_frame, text="Enable persistent device tracking", 
                       variable=self.persist_var).pack(anchor="w", pady=2)
        
        ttk.Label(persist_frame, text="Device history is stored in your user data directory", 
                 font=("", 9)).pack(anchor="w", pady=2)
        
        # Performance
        perf_frame = ttk.LabelFrame(parent, text="Performance", padding=10)
        perf_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        
        ttk.Label(perf_frame, text="Max concurrent scans:").grid(row=0, column=0, sticky="w", pady=5)
        self.max_threads_var = tk.IntVar(value=self.temp_settings.get("max_threads", 1))
        threads_spin = ttk.Spinbox(perf_frame, from_=1, to=10, textvariable=self.max_threads_var, width=10)
        threads_spin.grid(row=0, column=1, sticky="w", pady=5)
        
    def _detect_networks(self) -> None:
        """Detect available networks."""
        try:
            detected = autodetect_network()
            networks = [detected, "192.168.1.0/24", "192.168.0.0/24", "10.0.0.0/24"]
            self.network_combo['values'] = networks
            self.network_var.set(detected)
            self.network_mode.set("manual")
            self._update_network_mode()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect networks: {e}")
            
    def _update_network_mode(self) -> None:
        """Update network controls based on mode."""
        if self.network_mode.get() == "auto":
            self.network_combo.state(['disabled'])
            self.network_var.set("auto")
        else:
            self.network_combo.state(['!disabled'])
            
    def _toggle_json(self) -> None:
        """Toggle JSON output controls."""
        if self.json_enabled_var.get():
            self.json_entry.state(['!disabled'])
            self.json_browse_btn.state(['!disabled'])
        else:
            self.json_entry.state(['disabled'])
            self.json_browse_btn.state(['disabled'])
            
    def _toggle_csv(self) -> None:
        """Toggle CSV output controls."""
        if self.csv_enabled_var.get():
            self.csv_entry.state(['!disabled'])
            self.csv_browse_btn.state(['!disabled'])
        else:
            self.csv_entry.state(['disabled'])
            self.csv_browse_btn.state(['disabled'])
            
    def _browse_file(self, var: tk.StringVar, file_type: str, pattern: str) -> None:
        """Browse for output file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=pattern[1:],
            filetypes=[(f"{file_type} files", pattern), ("All files", "*.*")]
        )
        if filename:
            var.set(filename)
            
    def _apply_settings(self) -> None:
        """Apply settings without closing."""
        self._save_settings()
        
    def _ok_settings(self) -> None:
        """Save settings and close."""
        self._save_settings()
        self.destroy()
        
    def _save_settings(self) -> None:
        """Save all settings."""
        self.settings["interval"] = self.interval_var.get()
        self.settings["autostart"] = self.autostart_var.get()
        self.settings["remove_stale"] = self.remove_stale_var.get()
        self.settings["notify_new"] = self.notify_new_var.get()
        self.settings["notify_change"] = self.notify_change_var.get()
        self.settings["network"] = self.network_var.get()
        self.settings["timeout"] = self.timeout_var.get()
        self.settings["json_path"] = self.json_path_var.get() if self.json_enabled_var.get() else ""
        self.settings["csv_path"] = self.csv_path_var.get() if self.csv_enabled_var.get() else ""
        self.settings["timestamp_files"] = self.timestamp_var.get()
        self.settings["verbose"] = self.verbose_var.get()
        self.settings["mac_lookup"] = self.mac_lookup_var.get()
        self.settings["use_persistence"] = self.persist_var.get()
        self.settings["max_threads"] = self.max_threads_var.get()
        
        # Notify parent window to save settings to disk
        if hasattr(self.master, '_save_settings_to_disk'):
            self.master._save_settings_to_disk()


class ModernNetworkMonitorGUI(tk.Tk):
    """Modern main window with improved UI/UX."""
    
    def __init__(self) -> None:
        super().__init__()
        self.title("LAN Scanner")
        self.geometry("1200x700")
        
        # Set modern theme
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Configure colors
        style.configure("Toolbar.TFrame", background="#f0f0f0")
        style.configure("Status.TLabel", background="#e0e0e0")
        style.configure("Success.TLabel", foreground="green")
        style.configure("Error.TLabel", foreground="red")
        
        # Load settings from disk or use defaults
        self.settings = self._load_settings()
        
        self._running = False
        self._devices_cache: list[Device] = []
        self._last_device_count = 0
        self.monitor: Optional[NetworkMonitor] = None
        self.online_only_var = tk.BooleanVar(value=False)
        
        self._create_menu()
        self._create_toolbar()
        self._create_main_content()
        self._create_status_bar()
        
        # Initialize monitor
        self._init_monitor()
        
        # Bind events
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Auto-start if configured
        if self.settings.get("autostart", False):
            self.after(100, self._start_scanning)
        
    def _create_menu(self) -> None:
        """Create menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export JSON...", command=self._export_json)
        file_menu.add_command(label="Export CSV...", command=self._export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Settings...", command=self._open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self._manual_refresh)
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Show Details Panel", command=self._toggle_details)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
    def _create_toolbar(self) -> None:
        """Create toolbar with controls."""
        toolbar = ttk.Frame(self, style="Toolbar.TFrame", padding=5)
        toolbar.pack(fill="x", side="top")
        
        # Control buttons
        self.start_btn = ttk.Button(toolbar, text="▶ Start", command=self._start_scanning, width=10)
        self.start_btn.pack(side="left", padx=2)
        
        self.stop_btn = ttk.Button(toolbar, text="■ Stop", command=self._stop_scanning, 
                                   state="disabled", width=10)
        self.stop_btn.pack(side="left", padx=2)
        
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=10)
        
        # Quick actions
        ttk.Button(toolbar, text="🔄 Refresh", command=self._manual_refresh, width=10).pack(side="left", padx=2)
        ttk.Button(toolbar, text="📷 Scan Once", command=self._one_shot_scan, width=12).pack(side="left", padx=2)
        ttk.Button(toolbar, text="⚙ Settings", command=self._open_settings, width=10).pack(side="left", padx=2)
        
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=10)
        
        # Search
        ttk.Label(toolbar, text="Search:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._filter_devices())
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=2)
        
        # Online filter  
        ttk.Separator(toolbar, orient="vertical").pack(side="right", fill="y", padx=10)
        self.online_only_var.trace("w", lambda *args: self._filter_devices())
        ttk.Checkbutton(toolbar, text="Online only", variable=self.online_only_var).pack(side="right", padx=5)
        
        # Device count
        self.device_count_label = ttk.Label(toolbar, text="0 devices")
        self.device_count_label.pack(side="right", padx=10)
        
    def _create_main_content(self) -> None:
        """Create main content area."""
        # Main paned window
        self.paned = ttk.PanedWindow(self, orient="horizontal")
        self.paned.pack(fill="both", expand=True)
        
        # Left: Device list
        list_frame = ttk.Frame(self.paned)
        self.paned.add(list_frame, weight=3)
        
        # Configure treeview
        columns = ("MAC Address", "IP Address", "Hostname", "Manufacturer", "First Seen", "Last Seen", "Status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        # Column configuration
        widths = [140, 110, 150, 150, 150, 150, 60]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_tree(c))
            self.tree.column(col, width=width)
            
        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Configure tags for styling
        self.tree.tag_configure("online", foreground="green")
        self.tree.tag_configure("new", background="#e6ffe6")
        self.tree.tag_configure("changed", background="#fff0e6")
        
        # Right-click context menu
        self.tree.bind("<Button-3>", self._show_context_menu)
        
        # Right: Details panel (hidden by default)
        self.details_frame = ttk.Frame(self.paned)
        self.details_visible = False
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_device_select)
        
    def _create_status_bar(self) -> None:
        """Create status bar."""
        status_frame = ttk.Frame(self, relief="sunken")
        status_frame.pack(fill="x", side="bottom")
        
        # Status label
        self.status_label = ttk.Label(status_frame, text="Ready", style="Status.TLabel")
        self.status_label.pack(side="left", padx=10, pady=2)
        
        # Progress bar (hidden by default)
        self.progress = ttk.Progressbar(status_frame, mode="indeterminate", length=100)
        
        # Last scan label
        self.last_scan_label = ttk.Label(status_frame, text="", style="Status.TLabel")
        self.last_scan_label.pack(side="right", padx=10, pady=2)
        
    def _init_monitor(self) -> None:
        """Initialize network monitor."""
        try:
            network = None if self.settings["network"] == "auto" else self.settings["network"]
            self.monitor = NetworkMonitor(
                network=network,
                remove_stale=self.settings["remove_stale"],
                verbose=self.settings["verbose"],
                use_persistence=self.settings["use_persistence"]
            )
            self._manual_refresh()
        except Exception as e:
            messagebox.showerror("Initialization Error", str(e))
            self.status_label.config(text=f"Error: {e}", style="Error.TLabel")
            
    def _start_scanning(self) -> None:
        """Start continuous scanning."""
        self._running = True
        self.start_btn.state(["disabled"])
        self.stop_btn.state(["!disabled"])
        self.status_label.config(text="Scanning...", style="Success.TLabel")
        self.progress.pack(side="left", padx=10, pady=2)
        self.progress.start(10)
        self._schedule_scan()
        
    def _stop_scanning(self) -> None:
        """Stop continuous scanning."""
        self._running = False
        self.start_btn.state(["!disabled"])
        self.stop_btn.state(["disabled"])
        self.status_label.config(text="Stopped", style="Status.TLabel")
        self.progress.stop()
        self.progress.pack_forget()
        
    def _schedule_scan(self) -> None:
        """Schedule next scan."""
        if not self._running:
            return
        threading.Thread(target=self._perform_scan, daemon=True).start()
        self.after(self.settings["interval"] * 1000, self._schedule_scan)
        
    def _perform_scan(self) -> None:
        """Perform network scan in background."""
        try:
            self.monitor.scan()
            self.after(0, self._update_device_list)
            self.after(0, lambda: self.last_scan_label.config(
                text=f"Last scan: {datetime.datetime.now().strftime('%H:%M:%S')}"
            ))
            
            # Save to configured output files if enabled
            self.after(0, self._save_output_files)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Scan Error", str(e)))
            self.after(0, lambda: self.status_label.config(text=f"Error: {e}", style="Error.TLabel"))
    
    def _save_output_files(self) -> None:
        """Save scan results to configured output files."""
        if not self.monitor:
            return
            
        # Handle JSON output
        json_path = self.settings.get("json_path", "")
        if json_path:
            try:
                if self.settings.get("timestamp_files", False):
                    base, ext = os.path.splitext(json_path)
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_path = f"{base}_{timestamp}{ext}"
                self.monitor.to_json(json_path)
            except Exception as e:
                messagebox.showerror("JSON Export Error", f"Failed to save JSON: {e}")
        
        # Handle CSV output
        csv_path = self.settings.get("csv_path", "")
        if csv_path:
            try:
                if self.settings.get("timestamp_files", False):
                    base, ext = os.path.splitext(csv_path)
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    csv_path = f"{base}_{timestamp}{ext}"
                self.monitor.to_csv(csv_path)
            except Exception as e:
                messagebox.showerror("CSV Export Error", f"Failed to save CSV: {e}")
            
    def _manual_refresh(self) -> None:
        """Manually refresh device list."""
        if self.monitor:
            self._update_device_list()
            
    def _update_device_list(self) -> None:
        """Update the device list display."""
        devices = self.monitor.devices() if self.monitor else []
        self._devices_cache = devices
        self._filter_devices()
        
    def _filter_devices(self) -> None:
        """Filter devices based on search."""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Get search term
        search = self.search_var.get().lower()
        
        # Get current time for online status
        now = datetime.datetime.now(datetime.timezone.utc)
        
        # Filter and display devices
        displayed = 0
        for device in sorted(self._devices_cache, key=lambda d: d.ip_address):
            # Check if device matches search
            if search and not any(search in str(val).lower() if val else "" for val in [
                device.mac_address, device.ip_address, device.hostname, device.manufacturer
            ]):
                continue
            
            # Filter online-only if requested
            if self.online_only_var.get() and (now - device.last_seen).seconds >= 120:
                continue
                
            # Format timestamps - convert from UTC to local time
            first_seen_local = device.date_added.replace(tzinfo=datetime.timezone.utc).astimezone()
            last_seen_local = device.last_seen.replace(tzinfo=datetime.timezone.utc).astimezone()
            first_seen = first_seen_local.strftime("%Y-%m-%d %H:%M:%S")
            last_seen = last_seen_local.strftime("%Y-%m-%d %H:%M:%S")
            
            # Handle None values for display
            hostname = device.hostname or "-"
            manufacturer = device.manufacturer or "-"
            
            # Determine status and tags
            if (now - device.last_seen).seconds < 120:
                status = "Online"
                tags = ("online",)
            else:
                status = "Offline"
                tags = ()
                
            # Check if new device
            if (now - device.date_added).seconds < 300:
                tags = tags + ("new",)
                # Show notification if enabled
                if self.settings.get("notify_new", True) and hasattr(self, '_last_device_count'):
                    if displayed > self._last_device_count:
                        self.after(0, lambda: messagebox.showinfo(
                            "New Device Found", 
                            f"New device discovered: {device.mac_address} ({device.ip_address})"
                        ))
                
            # Insert into tree
            self.tree.insert("", "end", values=(
                device.mac_address,
                device.ip_address,
                hostname,
                manufacturer,
                first_seen,
                last_seen,
                status
            ), tags=tags)
            displayed += 1
            
        # Update count with online status
        total = len(self._devices_cache)
        online_total = sum(1 for d in self._devices_cache if (now - d.last_seen).seconds < 120)
        
        if self.online_only_var.get():
            self.device_count_label.config(text=f"{displayed} online devices")
        elif displayed < total:
            self.device_count_label.config(text=f"{displayed} of {total} devices ({online_total} online)")
        else:
            self.device_count_label.config(text=f"{total} devices ({online_total} online)")
        
        # Store count for new device notifications
        self._last_device_count = displayed
            
    def _sort_tree(self, column: str) -> None:
        """Sort treeview by column."""
        # Get all items
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children()]
        
        # Sort
        items.sort()
        
        # Rearrange
        for index, (_, item) in enumerate(items):
            self.tree.move(item, "", index)
            
    def _on_device_select(self, event: tk.Event) -> None:
        """Handle device selection."""
        selection = self.tree.selection()
        if selection and self.details_visible:
            # Update details panel
            item = self.tree.item(selection[0])
            # TODO: Update details panel with device info
            
    def _toggle_details(self) -> None:
        """Toggle details panel visibility."""
        if self.details_visible:
            self.paned.forget(self.details_frame)
            self.details_visible = False
        else:
            self.paned.add(self.details_frame, weight=1)
            self.details_visible = True
            
    def _open_settings(self) -> None:
        """Open settings dialog."""
        dialog = ModernSettingsDialog(self, self.settings)
        self.wait_window(dialog)
        # Reinitialize monitor if settings changed
        self._init_monitor()
        
    def _export_json(self) -> None:
        """Export to JSON file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename and self.monitor:
            self.monitor.to_json(filename)
            messagebox.showinfo("Export Complete", f"Exported to {filename}")
            
    def _export_csv(self) -> None:
        """Export to CSV file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename and self.monitor:
            self.monitor.to_csv(filename)
            messagebox.showinfo("Export Complete", f"Exported to {filename}")
            
    def _show_about(self) -> None:
        """Show about dialog."""
        messagebox.showinfo("About LAN Scanner", 
                           "LAN Scanner v0.2-beta\n\n"
                           "A modern network discovery tool\n\n"
                           "Built with Python and Tkinter")
        
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from disk or return defaults."""
        settings_file = get_user_data_dir() / "gui_settings.json"
        
        default_settings = {
            "interval": 30,
            "autostart": False,
            "remove_stale": False,
            "notify_new": True,
            "notify_change": False,
            "network": "auto",
            "timeout": 300,
            "json_path": "",
            "csv_path": "",
            "timestamp_files": False,
            "verbose": False,
            "mac_lookup": True,
            "use_persistence": True,
            "max_threads": 1,
        }
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to handle new settings
                    default_settings.update(loaded_settings)
            except Exception as e:
                print(f"Failed to load settings: {e}")
        
        return default_settings
    
    def _save_settings_to_disk(self) -> None:
        """Save settings to disk."""
        settings_file = get_user_data_dir() / "gui_settings.json"
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")
    
    def _one_shot_scan(self) -> None:
        """Perform a single scan and save to timestamped file."""
        if not self.monitor:
            messagebox.showerror("Error", "Monitor not initialized")
            return
            
        try:
            # Show progress
            self.status_label.config(text="Performing one-shot scan...", style="Status.TLabel")
            self.progress.pack(side="left", padx=10, pady=2)
            self.progress.start(10)
            
            # Perform scan in background
            def do_scan():
                self.monitor.scan()
                
                # Save to timestamped file
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                json_file = f"devices_{timestamp}.json"
                self.monitor.to_json(json_file)
                
                self.after(0, lambda: self._update_device_list())
                self.after(0, lambda: self.progress.stop())
                self.after(0, lambda: self.progress.pack_forget())
                self.after(0, lambda: self.status_label.config(
                    text=f"Scan complete. Saved to {json_file}", 
                    style="Success.TLabel"
                ))
                self.after(0, lambda: messagebox.showinfo(
                    "Scan Complete", 
                    f"One-shot scan completed.\nResults saved to: {json_file}"
                ))
                
            threading.Thread(target=do_scan, daemon=True).start()
            
        except Exception as e:
            self.progress.stop()
            self.progress.pack_forget()
            messagebox.showerror("Scan Error", str(e))
            self.status_label.config(text=f"Error: {e}", style="Error.TLabel")
    
    def _show_context_menu(self, event: tk.Event) -> None:
        """Show context menu for device actions."""
        # Select the item under cursor
        item = self.tree.identify_row(event.y)
        if not item:
            return
            
        self.tree.selection_set(item)
        
        # Create context menu
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Copy MAC Address", command=lambda: self._copy_device_info("MAC Address"))
        menu.add_command(label="Copy IP Address", command=lambda: self._copy_device_info("IP Address"))
        menu.add_command(label="Copy Hostname", command=lambda: self._copy_device_info("Hostname"))
        menu.add_separator()
        menu.add_command(label="Copy All Info", command=self._copy_all_device_info)
        
        # Show menu
        menu.tk_popup(event.x_root, event.y_root)
        menu.grab_release()
    
    def _copy_device_info(self, column: str) -> None:
        """Copy specific device information to clipboard."""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        values = item['values']
        
        # Map column name to index
        columns = ("MAC Address", "IP Address", "Hostname", "Manufacturer", "First Seen", "Last Seen", "Status")
        try:
            idx = columns.index(column)
            value = values[idx]
            
            # Copy to clipboard
            self.clipboard_clear()
            self.clipboard_append(str(value))
            self.update()
            
            self.status_label.config(text=f"Copied {column} to clipboard", style="Success.TLabel")
        except (ValueError, IndexError):
            pass
    
    def _copy_all_device_info(self) -> None:
        """Copy all device information to clipboard."""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        values = item['values']
        
        # Format all info
        info = f"""MAC Address: {values[0]}
IP Address: {values[1]}
Hostname: {values[2]}
Manufacturer: {values[3]}
First Seen: {values[4]}
Last Seen: {values[5]}
Status: {values[6]}"""
        
        # Copy to clipboard
        self.clipboard_clear()
        self.clipboard_append(info)
        self.update()
        
        self.status_label.config(text="Copied device info to clipboard", style="Success.TLabel")
    
    def _on_close(self) -> None:
        """Handle window close."""
        if self._running:
            self._stop_scanning()
        self._save_settings_to_disk()
        self.destroy()


def main() -> None:
    """Entry point for the modern GUI."""
    app = ModernNetworkMonitorGUI()
    app.mainloop()


if __name__ == "__main__":
    main()