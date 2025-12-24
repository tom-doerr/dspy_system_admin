"""Tests for DSPy agent with mocked LLM."""
import pytest
from unittest.mock import patch, MagicMock
from sysadmin.agent import SysAdminAgent, NetworkDiagnoser
from sysadmin.signatures import DiagnosisResult, ActionDecision


class TestAgentNoneHandling:
    def test_agent_raises_on_none_diagnosis(self):
        """Agent should raise RuntimeError when diagnoser returns None."""
        agent = SysAdminAgent()
        with patch.object(agent.diagnoser, "forward", return_value=None):
            with pytest.raises(RuntimeError, match="LLM returned None"):
                agent("wlP9s9", "up", 6.0, 258.0, -45)


class TestAgentWithMockedLLM:
    def test_no_issue_returns_none_action(self):
        """When no issue detected, action should be 'none'."""
        agent = SysAdminAgent()
        no_issue = DiagnosisResult(
            issue_detected=False, issue_type="none", severity="none"
        )
        with patch.object(agent.diagnoser, "forward", return_value=no_issue):
            diag, dec, reason = agent("wlP9s9", "up", 500.0, 500.0, -45)
            assert dec.action == "none"
