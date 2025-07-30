# simple‑lan‑scanner

> Lightweight LAN discovery tool written in Python.  
> **Status:** 🚧 *alpha – actively developed* 🚧

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## ⭐ Current capabilities (v0.1‑alpha)

| Feature | Details |
|---------|---------|
| **Ping‑sweep scan via Nmap** | Enumerates every host on your `/24` network (requires the `nmap` binary in `PATH`). |
| **Device inventory** | Collects `MAC`, `IP`, `first_seen`, `last_seen`. |
| **JSON / CSV export** | `lan-scan scan -o snapshot.json` or `devices.csv`. |
| **CLI** (`lan‑scan`) | One‑shot scan and continuous monitor loop. |
| **Tkinter GUI (early)** | Start/stop scans, set interval, view live table. |
| **Python API** | `from simple_scanner import NetworkMonitor` for embedding in other code. |

---

## 🚀 Quick start

```bash
git clone https://github.com/<your‑user>/simple-lan-scanner.git
cd simple-lan-scanner
python -m venv .venv && source .venv/bin/activate  # Win: .venv\Scripts\activate
pip install -e .[cli]

# install Nmap first ↓
# Windows 10/11:   winget install -e --id Insecure.Nmap
# Debian/Ubuntu :  sudo apt install nmap

# run a one‑shot scan
lan-scan scan -o devices.json --verbose

# start GUI
lan-scan gui