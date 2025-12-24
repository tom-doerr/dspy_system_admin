"""DSPy Modules for system admin agent."""
from __future__ import annotations
import json
import logging
import dspy

log = logging.getLogger(__name__)
from .signatures import DiagnoseNetwork, DecideAction
from .signatures import DiagnosisResult, ActionDecision
from .constants import KNOWN_WIFI_ISSUES, ALLOWED_ACTIONS


class NetworkDiagnoser(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(DiagnoseNetwork)

    def forward(self, interface: str, state: str,
                rx_mbps: float, tx_mbps: float, signal: int,
                known_issues: str = KNOWN_WIFI_ISSUES):
        r = self.predict(interface=interface, state=state,
                         rx_mbps=rx_mbps, tx_mbps=tx_mbps,
                         signal=signal, known_issues=known_issues)
        if r.diagnosis is None:
            log.error(f"DSPy returned None. Raw: {r}")
        return r.diagnosis


class ActionDecider(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(DecideAction)

    def forward(self, diagnosis: DiagnosisResult):
        actions = json.dumps(list(ALLOWED_ACTIONS.keys()))
        r = self.predict(diagnosis_json=diagnosis.model_dump_json(),
                         allowed_actions=actions)
        return r.decision, r.reasoning


class SysAdminAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.diagnoser = NetworkDiagnoser()
        self.decider = ActionDecider()

    def forward(self, interface: str, state: str,
                rx_mbps: float, tx_mbps: float, signal: int):
        diag = self.diagnoser(interface, state, rx_mbps, tx_mbps, signal)
        if diag is None:
            raise RuntimeError("LLM returned None diagnosis")
        if not diag.issue_detected:
            none = ActionDecision(action="none", confidence=1.0)
            return diag, none, "No issue"
        dec, reason = self.decider(diag)
        return diag, dec, reason


def configure_ollama(model: str = "qwen3:1.7b", temp: float = 0.0):
    """Configure DSPy to use local Ollama."""
    lm = dspy.LM(f"ollama_chat/{model}", temperature=temp, max_tokens=512)
    dspy.configure(lm=lm)
