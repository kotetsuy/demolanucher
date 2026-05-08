#!/bin/bash
# パスワードなしでシャットダウンできるように sudoers を設定するスクリプト
# 初回のみ sudo で実行: sudo bash setup_sudoers.sh

set -e

USERNAME="${SUDO_USER:-$(whoami)}"
SUDOERS_FILE="/etc/sudoers.d/demo-launcher-shutdown"

if [ "$EUID" -ne 0 ]; then
    echo "このスクリプトは sudo で実行してください:"
    echo "  sudo bash setup_sudoers.sh"
    exit 1
fi

cat > "$SUDOERS_FILE" <<EOF
# Demo Launcher: $USERNAME がパスワードなしでシャットダウンできるようにする
$USERNAME ALL=(ALL) NOPASSWD: /sbin/shutdown, /usr/sbin/shutdown
EOF

chmod 440 "$SUDOERS_FILE"
visudo -c -f "$SUDOERS_FILE"

echo "✓ 設定完了: $USERNAME はパスワードなしでシャットダウンできます"
echo "  ファイル: $SUDOERS_FILE"
