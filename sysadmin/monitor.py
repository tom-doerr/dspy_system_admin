"""Network monitor for WiFi health."""
from __future__ import annotations
import logging
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

log = logging.getLogger(__name__)


@dataclass
class Metrics:
    interface: str
    state: str
    rx_mbps: float
    tx_mbps: float
    signal: int


class NetworkMonitor:
    def __init__(self, iface: str, interval: float = 10.0,
                 rx_threshold: float = 10.0, ratio_threshold: float = 10.0):
        self.iface = iface
        self.interval = interval
        self.rx_thresh = rx_threshold
        self.ratio_thresh = ratio_threshold
        self._running = False

    def _get_state(self) -> str:
        p = Path(f"/sys/class/net/{self.iface}/operstate")
        try:
            return p.read_text().strip()
        except Exception:
            return "unknown"

    def _get_link_info(self) -> tuple[float, float, int]:
        try:
            r = subprocess.run(["iw", "dev", self.iface, "link"],
                               capture_output=True, text=True, timeout=5)
            out = r.stdout
        except Exception:
            return 0.0, 0.0, -100
        rx = re.search(r"rx bitrate:\s+([\d.]+)", out)
        tx = re.search(r"tx bitrate:\s+([\d.]+)", out)
        sig = re.search(r"signal:\s+(-?\d+)", out)
        return (float(rx.group(1)) if rx else 0.0,
                float(tx.group(1)) if tx else 0.0,
                int(sig.group(1)) if sig else -100)

    def collect(self) -> Metrics:
        state = self._get_state()
        rx, tx, sig = self._get_link_info()
        return Metrics(self.iface, state, rx, tx, sig)

    def detect_anomaly(self, m: Metrics) -> bool:
        if m.state != "up":
            log.info(f"Anomaly: state={m.state}")
            return True
        if m.rx_mbps < self.rx_thresh and m.tx_mbps > 0:
            ratio = m.tx_mbps / max(m.rx_mbps, 0.1)
            if ratio > self.ratio_thresh:
                log.info(f"Anomaly: TX/RX={ratio:.1f}")
                return True
        return False

    def run_loop(self, on_anomaly: Callable[[Metrics], None]):
        self._running = True
        log.info(f"Starting monitor for {self.iface}")
        while self._running:
            m = self.collect()
            if self.detect_anomaly(m):
                on_anomaly(m)
            time.sleep(self.interval)

    def stop(self):
        self._running = False
