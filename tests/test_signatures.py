"""Tests for Pydantic signature models."""
import pytest
from sysadmin.signatures import DiagnosisResult, ActionDecision


class TestActionDecision:
    def test_confidence_clamped_to_max(self):
        d = ActionDecision(action="wifi_reset", confidence=1.5)
        assert d.confidence == 1.0

    def test_confidence_clamped_to_min(self):
        d = ActionDecision(action="wifi_reset", confidence=-0.5)
        assert d.confidence == 0.0

    def test_confidence_none_becomes_zero(self):
        d = ActionDecision(action="wifi_reset", confidence=None)
        assert d.confidence == 0.0

    def test_valid_confidence_unchanged(self):
        d = ActionDecision(action="wifi_reset", confidence=0.8)
        assert d.confidence == 0.8


class TestDiagnosisResult:
    def test_creates_valid_diagnosis(self):
        d = DiagnosisResult(
            issue_detected=True, issue_type="wifi_rx_degraded", severity="critical"
        )
        assert d.issue_detected is True
        assert d.issue_type == "wifi_rx_degraded"
