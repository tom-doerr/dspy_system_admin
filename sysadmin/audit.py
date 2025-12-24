"""JSONL audit logger for security compliance."""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

DEFAULT_PATH = "~/.local/share/sysadmin/audit.jsonl"


class AuditLogger:
    def __init__(self, path: str = DEFAULT_PATH):
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _write(self, record: dict):
        record["ts"] = datetime.now().isoformat()
        with self.path.open("a") as f:
            f.write(json.dumps(record) + "\n")

    def log_intent(self, action: str, params: dict, cmd: list, reason: str):
        self._write({"event": "intent", "action": action,
                     "params": params, "cmd": " ".join(cmd), "reason": reason})

    def log_action(self, action: str, success: bool, rc: int, reason: str):
        self._write({"event": "action", "action": action,
                     "success": success, "rc": rc, "reason": reason})

    def log_decision(self, diag: dict, decision: dict, reason: str):
        self._write({"event": "decision", "diag": diag,
                     "decision": decision, "reason": reason})
