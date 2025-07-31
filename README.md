# simple‑lan‑scanner

> Lightweight LAN discovery tool written in Python.  
> **Status:** 🚀 *v0.2-beta – production ready* 🚀

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## ⭐ Current capabilities (v0.2‑beta)

| Feature | Details |
|---------|---------|
| **Ping‑sweep scan via Nmap** | Enumerates every host on your `/24` network (requires the `nmap` binary in `PATH`). |
| **Device inventory** | Collects `MAC`, `IP`, `first_seen`, `last_seen` with persistent storage. |
| **Persistent data storage** | Core device data stored in user data directory (`%APPDATA%/simple-lan-scanner/` on Windows, `~/.simple-lan-scanner/` on Unix). |
| **JSON / CSV export** | `lan-scan scan -o snapshot.json` or `devices.csv` with flexible output options. |
| **CLI** (`lan‑scan`) | One‑shot scan and continuous monitor loop with clean file organization. |
| **Tkinter GUI (experimental)** | Start/stop scans, set interval, view live table. Early development stage. |
| **Python API** | `from simple_scanner import NetworkMonitor` for embedding in other code. |

---

## 🚀 Quick start

```bash
git clone https://github.com/IBN5100-0/simple-lan-scanner.git
cd simple-lan-scanner
python -m venv .venv && source .venv/bin/activate  # Win: .venv\Scripts\activate
pip install -e .[cli]

# install Nmap first ↓
# Windows 10/11:   winget install -e --id Insecure.Nmap
# Debian/Ubuntu :  sudo apt install nmap

# run a one‑shot scan
lan-scan scan -o devices.json --verbose

# monitor network continuously
lan-scan monitor --interval 60 --verbose

# start GUI (experimental)
lan-scan gui