#!/bin/bash
# Install sysadmin agent with root-owned source (prevents privilege escalation)
set -e

INSTALL_DIR="/usr/local/lib/sysadmin"
BIN_DIR="/usr/local/bin"

echo "Installing sysadmin agent..."

# Must run as root
if [[ $EUID -ne 0 ]]; then
    echo "Run as root: sudo $0"
    exit 1
fi

# Create install directory (root-owned)
mkdir -p "$INSTALL_DIR"
cp -r sysadmin/* "$INSTALL_DIR/"
chown -R root:root "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"
chmod 644 "$INSTALL_DIR"/*.py

# Create launcher script (root-owned)
cat > "$BIN_DIR/sysadmin" << 'LAUNCHER'
#!/usr/bin/env python3
import sys
sys.path.insert(0, "/usr/local/lib")
from sysadmin.cli import main
main()
LAUNCHER
chown root:root "$BIN_DIR/sysadmin"
chmod 755 "$BIN_DIR/sysadmin"

# Install sudoers (minimal privileges)
cp config/sysadmin.sudoers /etc/sudoers.d/sysadmin
chown root:root /etc/sudoers.d/sysadmin
chmod 440 /etc/sudoers.d/sysadmin

echo "Installed:"
echo "  Source: $INSTALL_DIR/ (root-owned, read-only to tom)"
echo "  Binary: $BIN_DIR/sysadmin"
echo "  Sudoers: /etc/sudoers.d/sysadmin"
echo ""
echo "Test: sysadmin list-actions"
echo "Daemon: sysadmin daemon --dry-run"
