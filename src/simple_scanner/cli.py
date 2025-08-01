import time
from pathlib import Path
from datetime import datetime

import click
from .scanner import NetworkMonitor


@click.group()
def app() -> None:
    """simple-lan-scanner."""


# ------------------------------------------------------------------ #
# one‑off scan (JSON / CSV snapshot)
# ------------------------------------------------------------------ #
@app.command(help="Scan once and write JSON/CSV")
@click.option(
    "--out",
    "-o",
    type=click.Path(dir_okay=False, writable=True),
    help="Output path (.json or .csv). Defaults to timestamped file.",
)
@click.option("--network", help="CIDR to scan (skip autodetect)")
@click.option("--verbose", is_flag=True, help="Print raw nmap output")
@click.option("--remove-stale", is_flag=True, help="Prune devices missing in scan")
def scan(out: str | None, network: str | None, verbose: bool, remove_stale: bool) -> None:
    # For scan command: use persistence to get date_added, but don't save back to core
    nm = NetworkMonitor(network=network, verbose=verbose, remove_stale=remove_stale, use_persistence=True)
    # Override use_persistence after loading to prevent saving during scan
    nm.use_persistence = False
    nm.scan()

    if out is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = f"devices_{stamp}.json"

    path = Path(out)
    if path.suffix == ".json":
        nm.to_json(path)
    elif path.suffix == ".csv":
        nm.to_csv(path)
    else:
        click.echo("❌  --out must end with .json or .csv", err=True)
        raise SystemExit(1)

    click.echo(f"✔  wrote {path.resolve()}")


# ------------------------------------------------------------------ #
# continuous monitor  (your old while‑True loop)
# ------------------------------------------------------------------ #
@app.command(help="Continuous scan every N seconds")
@click.option("--interval", type=click.IntRange(5, 3600), default=30, show_default=True)
@click.option("--network", help="CIDR to scan (skip autodetect)")
@click.option("--json", "json_path", type=click.Path(dir_okay=False))
@click.option("--csv",  "csv_path",  type=click.Path(dir_okay=False))
@click.option("--verbose", is_flag=True)
@click.option("--remove-stale", is_flag=True)
@click.option("--online-only", is_flag=True, help="Show only online devices")
@click.option("--search", help="Filter devices by MAC, IP, hostname, or manufacturer")
def monitor(
    interval: int,
    network: str | None,
    json_path: str | None,
    csv_path: str | None,
    verbose: bool,
    remove_stale: bool,
    online_only: bool,
    search: str | None,
) -> None:
    # Only create output files if explicitly requested (no defaults)

    # For monitor mode, always use persistence
    nm = NetworkMonitor(network=network, verbose=verbose, remove_stale=remove_stale, use_persistence=True)
    click.echo(f"Scanning {nm.network} every {interval}s – Ctrl‑C to stop")

    try:
        while True:
            nm.scan()  # This automatically saves to core data file
            
            # Display devices in a formatted table
            devices = nm.devices()
            
            # Filter by search term if provided
            if search:
                search_lower = search.lower()
                devices = [d for d in devices if any(
                    search_lower in str(getattr(d, attr, "") or "").lower() 
                    for attr in ["mac_address", "ip_address", "hostname", "manufacturer"]
                )]
            
            # Filter online-only if requested
            if online_only:
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc)
                devices = [d for d in devices if (now - d.last_seen).total_seconds() < 120]
            
            if devices:
                # Count online devices
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc)
                online_count = sum(1 for d in devices if (now - d.last_seen).total_seconds() < 120)
                
                click.echo("\n" + nm.get_device_header())
                for d in sorted(devices, key=lambda x: x.ip_address):
                    # Add status indicator
                    if (now - d.last_seen).total_seconds() < 120:
                        click.echo(click.style(str(d), fg="green"))
                    else:
                        click.echo(d)
                
                if online_only:
                    click.echo(f"\nOnline devices: {len(devices)}")
                else:
                    click.echo(f"\nTotal devices: {len(devices)} ({online_count} online)")
            else:
                if search:
                    click.echo(f"No devices found matching '{search}'.")
                else:
                    click.echo("No devices found.")
            
            # Save to user-specified output files
            if json_path:
                nm.to_json(json_path)  
                if verbose:
                    click.echo(f"Saved JSON → {json_path}")
            if csv_path:
                nm.to_csv(csv_path)
                if verbose:
                    click.echo(f"Saved CSV  → {csv_path}")
            time.sleep(interval)
    except KeyboardInterrupt:
        click.secho("\nStopped by user.", fg="yellow")
    except Exception as exc:
        click.secho(f"Error: {exc}", fg="red", err=True)
        raise SystemExit(1)


@app.command(help="Launch the GUI application")
def gui() -> None:
    """Launch the graphical user interface."""
    try:
        from .gui import main
        main()
    except ImportError as e:
        click.secho("GUI dependencies not available. Install with: pip install tkinter", fg="red", err=True)
        raise SystemExit(1) from e
    except Exception as exc:
        click.secho(f"GUI Error: {exc}", fg="red", err=True)
        raise SystemExit(1)


