"""DSPy Signatures for system admin agent."""
from __future__ import annotations
import dspy
from pydantic import BaseModel, field_validator


class DiagnosisResult(BaseModel):
    issue_detected: bool
    issue_type: str  # wifi_rx_degraded, interface_down, none
    severity: str    # critical, warning, none


class ActionDecision(BaseModel):
    action: str       # from whitelist or "none"
    confidence: float

    @field_validator("confidence", mode="before")
    @classmethod
    def clamp(cls, v):
        return max(0.0, min(1.0, float(v or 0)))


class DiagnoseNetwork(dspy.Signature):
    """Analyze network metrics and diagnose issues."""
    interface: str = dspy.InputField(desc="Interface name")
    state: str = dspy.InputField(desc="up/down/dormant")
    rx_mbps: float = dspy.InputField(desc="RX bitrate Mbit/s")
    tx_mbps: float = dspy.InputField(desc="TX bitrate Mbit/s")
    signal: int = dspy.InputField(desc="Signal dBm")
    known_issues: str = dspy.InputField(desc="Known driver bugs")
    diagnosis: DiagnosisResult = dspy.OutputField()


class DecideAction(dspy.Signature):
    """Decide action from whitelist based on diagnosis."""
    diagnosis_json: str = dspy.InputField(desc="JSON diagnosis")
    allowed_actions: str = dspy.InputField(desc="JSON whitelist")
    decision: ActionDecision = dspy.OutputField()
    reasoning: str = dspy.OutputField(desc="Brief explanation")
