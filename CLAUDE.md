# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Development
python -m sysadmin list-actions
python -m sysadmin action wifi_reset --dry-run
python -m sysadmin daemon --dry-run

# Tests
python3 -m pytest tests/ -v

# DSPy optimization
python3 -m sysadmin.optimize

# Production install (root-owned)
sudo ./install.sh
```

## Architecture

DSPy agent monitors WiFi, auto-recovers from MT7925 driver bugs.

```
Monitor → DSPy Agent → Executor → sudo
         (Ollama)      (whitelist)
```

**Flow:**
1. `monitor.py` polls sysfs + `iw` for RX/TX bitrates
2. Anomaly: RX < 10 Mbps, TX/RX ratio > 10
3. `agent.py` DSPy chain: DiagnoseNetwork → DecideAction
4. `executor.py` validates against `ALLOWED_ACTIONS`
5. Runs `sudo -n /usr/sbin/ip link set wlP9s9 down/up`

**DSPy:** Signatures in `signatures.py` (Pydantic output models), Modules in `agent.py`. LLM: Ollama `qwen3:1.7b`.

## Security Model

Prevents privilege escalation via root-owned source:
- Source at `/usr/local/lib/sysadmin/` (root-owned)
- `ALLOWED_ACTIONS` whitelist in `constants.py`
- Sudoers restricts to exact `ip link` commands
- Confidence threshold > 0.7 to execute

## Tests

19 tests in `tests/`:
- `test_executor.py` - Whitelist validation, injection blocking
- `test_monitor.py` - Anomaly detection for MT7925 bug
- `test_signatures.py` - Pydantic validators (confidence clamping)
- `test_agent.py` - Mocked LLM, None handling

## DSPy Optimization

- `dataset.py` - `generate_examples(n)` creates n×3 examples programmatically
- `optimize.py` - BootstrapFewShot optimization
- Classes: healthy, wifi_rx_degraded, interface_down

**Accuracy with qwen3:1.7b:** 42% baseline → 58% after SIMBA optimization

**SIMBA optimizer:** `optimize_simba(model, n)` - slower but learns rules
- sglang not supported on GB10 (sm_121)
- ~10min per batch with Ollama

## WiFi Watchdog Service

Simple systemd service that resets WiFi when connection is lost.

```bash
systemctl --user status wifi-watchdog
journalctl --user -u wifi-watchdog -f
```

**Config:** `config/wifi-watchdog.service`, `config/sudoers-sysadmin`

**Behavior:** Pings gateway every 10s, resets after 3 failures, 60s cooldown.

## Known Issues

**DSPy 3.0.4 returns None intermittently:**
- `dspy.Predict` returns `Prediction(diagnosis=None)` when parsing fails
- Agent raises `RuntimeError`, CLI catches and continues
- Happens ~40% of calls with qwen3:1.7b (major accuracy killer)
- Likely improves with larger models
