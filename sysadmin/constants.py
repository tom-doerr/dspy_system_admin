"""Constants for sysadmin agent."""

DEFAULT_OLLAMA_MODEL = "qwen3:1.7b"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 512
DEFAULT_INTERFACE = "wlP9s9"
DEFAULT_POLL_INTERVAL = 10.0
DEFAULT_COOLDOWN = 300
DEFAULT_RX_THRESHOLD = 10.0
DEFAULT_TX_RX_RATIO = 10.0
CONFIDENCE_THRESHOLD = 0.7

ALLOWED_ACTIONS = {
    "wifi_reset": {
        "desc": "Reset WiFi (down then up)",
        "cmds": ["/usr/sbin/ip link set {iface} down",
                 "/usr/sbin/ip link set {iface} up"],
        "ifaces": ["wlP9s9"],
    },
    "wifi_down": {
        "desc": "Bring WiFi down",
        "cmds": ["/usr/sbin/ip link set {iface} down"],
        "ifaces": ["wlP9s9"],
    },
    "wifi_up": {
        "desc": "Bring WiFi up",
        "cmds": ["/usr/sbin/ip link set {iface} up"],
        "ifaces": ["wlP9s9"],
    },
}

KNOWN_WIFI_ISSUES = """MediaTek MT7925 driver bugs:
1. RX rate drops to 6 Mbit/s while TX stays normal (576+ Mbit/s)
2. Recovery: interface reset (down/up) fixes it
"""
