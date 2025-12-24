"""Training dataset for DSPy optimization."""
import random
from sysadmin.signatures import DiagnosisResult


def _make(state, rx, tx, signal, issue, itype, sev):
    return {
        "inputs": {
            "interface": "wlP9s9", "state": state,
            "rx_mbps": round(rx, 1), "tx_mbps": round(tx, 1),
            "signal": signal,
        },
        "output": DiagnosisResult(
            issue_detected=issue, issue_type=itype, severity=sev
        ),
    }


def generate_examples(n: int = 5, seed: int = 42):
    """Generate training examples programmatically."""
    random.seed(seed)
    ex = []
    for _ in range(n):
        # Healthy
        ex.append(_make("up", random.uniform(200, 800),
                        random.uniform(200, 800),
                        random.randint(-60, -40),
                        False, "none", "none"))
        # MT7925 bug: RX stuck low, TX normal
        ex.append(_make("up", random.uniform(1, 10),
                        random.uniform(150, 600),
                        random.randint(-55, -40),
                        True, "wifi_rx_degraded", "critical"))
        # Interface down
        ex.append(_make("down", 0.0, 0.0,
                        random.randint(-100, -90),
                        True, "interface_down", "critical"))
    return ex


DIAGNOSE_EXAMPLES = [
    # Healthy states
    {
        "inputs": {
            "interface": "wlP9s9",
            "state": "up",
            "rx_mbps": 500.0,
            "tx_mbps": 520.0,
            "signal": -45,
        },
        "output": DiagnosisResult(
            issue_detected=False, issue_type="none", severity="none"
        ),
    },
    # MT7925 driver bug - RX stuck at 6 Mbps
    {
        "inputs": {
            "interface": "wlP9s9",
            "state": "up",
            "rx_mbps": 6.0,
            "tx_mbps": 258.0,
            "signal": -45,
        },
        "output": DiagnosisResult(
            issue_detected=True, issue_type="wifi_rx_degraded", severity="critical"
        ),
    },
    # Interface down
    {
        "inputs": {
            "interface": "wlP9s9",
            "state": "down",
            "rx_mbps": 0.0,
            "tx_mbps": 0.0,
            "signal": -100,
        },
        "output": DiagnosisResult(
            issue_detected=True, issue_type="interface_down", severity="critical"
        ),
    },
    # Another healthy example
    {
        "inputs": {
            "interface": "wlP9s9",
            "state": "up",
            "rx_mbps": 720.0,
            "tx_mbps": 576.0,
            "signal": -50,
        },
        "output": DiagnosisResult(
            issue_detected=False, issue_type="none", severity="none"
        ),
    },
]


def to_dspy_examples(n: int = 5, seed: int = 42):
    """Convert generated examples to DSPy Example format."""
    import dspy
    from .constants import KNOWN_WIFI_ISSUES
    examples = []
    for ex in generate_examples(n, seed):
        inp = {**ex["inputs"], "known_issues": KNOWN_WIFI_ISSUES}
        examples.append(dspy.Example(diagnosis=ex["output"], **inp).with_inputs(
            "interface", "state", "rx_mbps", "tx_mbps", "signal", "known_issues"
        ))
    return examples
