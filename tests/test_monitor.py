"""Tests for network monitor anomaly detection."""
import pytest
from sysadmin.monitor import NetworkMonitor, Metrics


@pytest.fixture
def monitor():
    return NetworkMonitor("wlP9s9", rx_threshold=10.0, ratio_threshold=10.0)


class TestAnomalyDetection:
    def test_healthy_no_anomaly(self, monitor):
        m = Metrics("wlP9s9", "up", rx_mbps=500.0, tx_mbps=500.0, signal=-45)
        assert monitor.detect_anomaly(m) is False

    def test_interface_down_is_anomaly(self, monitor):
        m = Metrics("wlP9s9", "down", rx_mbps=0.0, tx_mbps=0.0, signal=-100)
        assert monitor.detect_anomaly(m) is True

    def test_mt7925_bug_detected(self, monitor):
        # Real MT7925 bug: RX stuck at 6 Mbps, TX normal
        m = Metrics("wlP9s9", "up", rx_mbps=6.0, tx_mbps=258.0, signal=-45)
        assert monitor.detect_anomaly(m) is True

    def test_low_rx_low_tx_no_anomaly(self, monitor):
        # Both low but ratio OK - not the driver bug
        m = Metrics("wlP9s9", "up", rx_mbps=5.0, tx_mbps=5.0, signal=-80)
        assert monitor.detect_anomaly(m) is False
