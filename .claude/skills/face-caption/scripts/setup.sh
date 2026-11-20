#!/usr/bin/env bash
# Installs what the face-caption skill needs. Safe to run repeatedly.
set -e
command -v ffmpeg >/dev/null || {
  echo "ffmpeg tidak ditemukan. Install dulu:"
  echo "  macOS:   brew install ffmpeg"
  echo "  Ubuntu:  sudo apt-get install -y ffmpeg"
  echo "  Windows: winget install Gyan.FFmpeg"
  exit 1
}
PY=${PYTHON:-python3}
"$PY" - <<'EOF' 2>/dev/null && { echo "[ok] semua dependency sudah ada"; exit 0; }
import numpy, PIL, cv2, faster_whisper, mediapipe
EOF
"$PY" -m pip install --quiet --upgrade numpy pillow opencv-python-headless faster-whisper mediapipe
echo "[ok] dependency terpasang"
