#!/usr/bin/env python3
"""Simple network watchdog - restarts WiFi when connection is lost."""
import argparse
import logging
import subprocess
import time

log = logging.getLogger(__name__)

DEFAULT_GATEWAY = "192.168.8.1"
DEFAULT_INTERFACE = "wlP9s9"
DEFAULT_INTERVAL = 10
DEFAULT_FAILURES = 3
DEFAULT_COOLDOWN = 60


def ping(host: str, timeout: int = 2) -> bool:
    """Return True if host is reachable."""
    try:
        subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), host],
            capture_output=True, check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def reset_wifi(iface: str) -> bool:
    """Reset WiFi interface (down then up)."""
    try:
        subprocess.run(
            ["sudo", "-n", "/usr/sbin/ip", "link", "set", iface, "down"],
            check=True
        )
        time.sleep(1)
        subprocess.run(
            ["sudo", "-n", "/usr/sbin/ip", "link", "set", iface, "up"],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        log.error(f"Reset failed: {e}")
        return False


def run(gateway: str, iface: str, interval: int, max_failures: int, cooldown: int):
    """Main watchdog loop."""
    failures = 0
    last_reset = 0
    log.info(f"Watching {iface}, pinging {gateway} every {interval}s")

    while True:
        if ping(gateway):
            if failures > 0:
                log.info("Connection restored")
            failures = 0
        else:
            failures += 1
            log.warning(f"Ping failed ({failures}/{max_failures})")

            if failures >= max_failures:
                now = time.time()
                if now - last_reset > cooldown:
                    log.warning(f"Connection lost, resetting {iface}")
                    if reset_wifi(iface):
                        log.info("Reset complete")
                        last_reset = now
                        failures = 0
                        time.sleep(10)
                else:
                    remain = int(cooldown - (now - last_reset))
                    log.info(f"Cooldown active, {remain}s remaining")

        time.sleep(interval)


def main():
    ap = argparse.ArgumentParser(description="Network watchdog")
    ap.add_argument("--gateway", default=DEFAULT_GATEWAY)
    ap.add_argument("--interface", default=DEFAULT_INTERFACE)
    ap.add_argument("--interval", type=int, default=DEFAULT_INTERVAL)
    ap.add_argument("--failures", type=int, default=DEFAULT_FAILURES)
    ap.add_argument("--cooldown", type=int, default=DEFAULT_COOLDOWN)
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s"
    )
    run(args.gateway, args.interface, args.interval, args.failures, args.cooldown)


if __name__ == "__main__":
    main()
