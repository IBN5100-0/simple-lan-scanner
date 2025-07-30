import argparse
import time
from scanner import NetworkMonitor


def main() -> None:
    """CLI for continuous nmap scanning with export options."""
    parser = argparse.ArgumentParser(description="Network nmap scanner")
    parser.add_argument(
        '--remove-stale', action='store_true', help='Remove devices not seen in latest scan'
    )
    parser.add_argument(
        '--verbose', action='store_true', help='Show raw nmap output'
    )
    parser.add_argument(
        '--json', type=str, default=None, help='Path to output JSON (defaults to devices.json)'
    )
    parser.add_argument(
        '--csv', type=str, default=None, help='Path to output CSV (defaults to devices.csv)'
    )
    parser.add_argument(
        '--interval', type=int, default=30, help='Scan interval in seconds'
    )
    args = parser.parse_args()

    if not args.json and not args.csv:
        args.json = 'devices.json'
        args.csv = 'devices.csv'

    monitor = NetworkMonitor(
        remove_stale=args.remove_stale,
        verbose=args.verbose,
    )
    print(f"Scanning network {monitor.network} every {args.interval}s...")

    try:
        while True:
            monitor.scan()
            for d in monitor.devices():
                print(d)
            if args.json:
                monitor.to_json(args.json)
                if args.verbose:
                    print(f"Exported JSON to {args.json}")
            if args.csv:
                monitor.to_csv(args.csv)
                if args.verbose:
                    print(f"Exported CSV to {args.csv}")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()

