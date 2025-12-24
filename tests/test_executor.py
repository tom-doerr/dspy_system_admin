"""Tests for secure executor whitelist validation."""
import pytest
from unittest.mock import MagicMock, patch
from sysadmin.executor import SecureExecutor
from sysadmin.audit import AuditLogger


@pytest.fixture
def mock_audit(tmp_path):
    return AuditLogger(str(tmp_path / "audit.jsonl"))


@pytest.fixture
def executor(mock_audit):
    return SecureExecutor(mock_audit, dry_run=True)


class TestWhitelistValidation:
    def test_allowed_action_builds_commands(self, executor):
        cmds = executor._build_cmds("wifi_reset", "wlP9s9")
        assert cmds is not None
        assert len(cmds) == 2

    def test_disallowed_action_returns_none(self, executor):
        cmds = executor._build_cmds("rm_rf_root", "wlP9s9")
        assert cmds is None

    def test_disallowed_interface_returns_none(self, executor):
        cmds = executor._build_cmds("wifi_reset", "eth0")
        assert cmds is None

    def test_injection_attempt_blocked(self, executor):
        cmds = executor._build_cmds("wifi_reset; rm -rf /", "wlP9s9")
        assert cmds is None

    def test_interface_injection_blocked(self, executor):
        cmds = executor._build_cmds("wifi_reset", "wlP9s9; rm -rf /")
        assert cmds is None


class TestExecute:
    def test_dry_run_succeeds(self, executor):
        result = executor.execute("wifi_reset", "wlP9s9", "test")
        assert result is True

    def test_disallowed_action_fails(self, executor):
        result = executor.execute("evil_command", "wlP9s9", "test")
        assert result is False

    @patch("subprocess.run")
    def test_real_exec_calls_subprocess(self, mock_run, mock_audit):
        mock_run.return_value = MagicMock(returncode=0)
        ex = SecureExecutor(mock_audit, dry_run=False)
        assert ex.execute("wifi_reset", "wlP9s9", "test") is True
        assert mock_run.call_count == 2
