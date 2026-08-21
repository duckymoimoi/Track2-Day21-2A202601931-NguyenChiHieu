#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <gcs-bucket>" >&2
  exit 2
fi

bucket="$1"
app_dir="$HOME/mlops-app"

sudo apt-get update
sudo apt-get install -y python3-venv
python3 -m venv "$app_dir/.venv"
"$app_dir/.venv/bin/python" -m pip install --upgrade pip
"$app_dir/.venv/bin/python" -m pip install -r "$app_dir/requirements-serve.txt"

sudo tee /etc/systemd/system/mlops-serve.service >/dev/null <<EOF
[Unit]
Description=MLOps Wine Quality Inference API
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$app_dir
Environment="GCS_BUCKET=$bucket"
ExecStart=$app_dir/.venv/bin/python $app_dir/src/serve.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable mlops-serve
echo "VM runtime and mlops-serve systemd unit configured."
