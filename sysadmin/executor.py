"""Secure executor for whitelisted sudo commands."""
from __future__ import annotations
import logging
import shlex
import subprocess
from .audit import AuditLogger
from .constants import ALLOWED_ACTIONS

log = logging.getLogger(__name__)


class SecureExecutor:
    def __init__(self, audit: AuditLogger, dry_run: bool = False):
        self.audit = audit
        self.dry_run = dry_run

    def _build_cmds(self, action: str, iface: str):
        if action not in ALLOWED_ACTIONS:
            log.warning(f"Action '{action}' not in whitelist")
            return None
        spec = ALLOWED_ACTIONS[action]
        if iface not in spec["ifaces"]:
            log.warning(f"Interface '{iface}' not allowed")
            return None
        result = []
        for c in spec["cmds"]:
            result.append(["/usr/bin/sudo", "-n"] + shlex.split(c.format(iface=iface)))
        return result

    def execute(self, action: str, iface: str, reason: str = "") -> bool:
        cmds = self._build_cmds(action, iface)
        if cmds is None:
            self.audit.log_action(action, False, -1, "not allowed")
            return False
        self.audit.log_intent(action, {"iface": iface}, cmds[0], reason)
        if self.dry_run:
            for cmd in cmds:
                log.info(f"DRY RUN: {' '.join(cmd)}")
            self.audit.log_action(action, True, 0, "dry run")
            return True
        for cmd in cmds:
            try:
                r = subprocess.run(cmd, capture_output=True, timeout=30)
                if r.returncode != 0:
                    self.audit.log_action(action, False, r.returncode, reason)
                    return False
            except Exception as e:
                log.error(f"Failed: {e}")
                self.audit.log_action(action, False, -1, str(e))
                return False
        self.audit.log_action(action, True, 0, reason)
        return True
