#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <base64-public-key>" >&2
  exit 2
fi

public_key="$(printf '%s' "$1" | base64 --decode)"
mkdir -p "$HOME/.ssh"
touch "$HOME/.ssh/authorized_keys"
if ! grep -qxF "$public_key" "$HOME/.ssh/authorized_keys"; then
  printf '%s\n' "$public_key" >> "$HOME/.ssh/authorized_keys"
fi
chmod 700 "$HOME/.ssh"
chmod 600 "$HOME/.ssh/authorized_keys"
