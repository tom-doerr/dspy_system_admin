"""CLI for sysadmin agent."""
from __future__ import annotations
import argparse
import logging
import sys

from .constants import DEFAULT_INTERFACE, DEFAULT_OLLAMA_MODEL
from .constants import ALLOWED_ACTIONS, CONFIDENCE_THRESHOLD

log = logging.getLogger(__name__)


def cmd_daemon(args):
    from .agent import SysAdminAgent, configure_ollama
    from .audit import AuditLogger
    from .executor import SecureExecutor
    from .monitor import NetworkMonitor

    configure_ollama(args.model)
    audit = AuditLogger()
    executor = SecureExecutor(audit, dry_run=args.dry_run)
    agent = SysAdminAgent()

    def on_anomaly(m):
        log.info(f"Anomaly: {m}")
        try:
            diag, dec, reason = agent(
                m.interface, m.state, m.rx_mbps, m.tx_mbps, m.signal
            )
        except RuntimeError as e:
            log.error(f"Agent failed: {e}")
            return
        audit.log_decision(diag.model_dump(), dec.model_dump(), reason)
        if dec.action != "none" and dec.confidence > CONFIDENCE_THRESHOLD:
            log.info(f"Executing: {dec.action} ({reason})")
            executor.execute(dec.action, args.interface, reason)

    mon = NetworkMonitor(args.interface, args.interval)
    try:
        mon.run_loop(on_anomaly)
    except KeyboardInterrupt:
        log.info("Shutting down...")
        mon.stop()


def cmd_action(args):
    from .audit import AuditLogger
    from .executor import SecureExecutor
    audit = AuditLogger()
    executor = SecureExecutor(audit, dry_run=args.dry_run)
    ok = executor.execute(args.name, args.interface, "manual")
    sys.exit(0 if ok else 1)


def cmd_list_actions(args):
    print("Allowed actions:")
    for name, spec in ALLOWED_ACTIONS.items():
        print(f"  {name}: {spec['desc']}")
        print(f"    interfaces: {spec['ifaces']}")


def main():
    ap = argparse.ArgumentParser(prog="sysadmin")
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # daemon
    p = sub.add_parser("daemon", help="Run monitor daemon")
    p.add_argument("--interface", default=DEFAULT_INTERFACE)
    p.add_argument("--interval", type=float, default=10.0)
    p.add_argument("--model", default=DEFAULT_OLLAMA_MODEL)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_daemon)

    # action
    p = sub.add_parser("action", help="Run specific action")
    p.add_argument("name", choices=list(ALLOWED_ACTIONS.keys()))
    p.add_argument("--interface", default=DEFAULT_INTERFACE)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_action)

    # list-actions
    p = sub.add_parser("list-actions", help="List allowed actions")
    p.set_defaults(func=cmd_list_actions)

    args = ap.parse_args()
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s: %(message)s")
    args.func(args)


if __name__ == "__main__":
    main()
