#!/usr/bin/env bash
# Installation sur un VPS Hostinger (Ubuntu 22.04/24.04), à lancer en root :
#   curl -fsSL <raw-url>/deploy/install.sh | bash   (ou bash deploy/install.sh depuis le dépôt)
# Installe FFmpeg + polices, crée l'utilisateur, le venv, les services systemd.
set -euo pipefail

APP_DIR=/opt/chronoshorts
REPO_URL="${REPO_URL:-https://github.com/aybbkf/wavecast.git}"
BRANCH="${BRANCH:-main}"
SUBDIR="${SUBDIR:-agency}"

echo "▶ Paquets système"
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  python3 python3-venv python3-pip git ffmpeg libass9 \
  fonts-dejavu-core fonts-noto-core fonts-noto-ui-core fonts-noto-color-emoji ca-certificates
fc-cache -f >/dev/null || true

echo "▶ Utilisateur et dossiers"
id -u chronoshorts >/dev/null 2>&1 || useradd --system --create-home --shell /usr/sbin/nologin chronoshorts
mkdir -p "$APP_DIR"

echo "▶ Code"
if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" pull --ff-only
else
  TMP=$(mktemp -d)
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$TMP/repo"
  if [ -d "$TMP/repo/$SUBDIR" ]; then
    cp -r "$TMP/repo/$SUBDIR/." "$APP_DIR/"
  else
    cp -r "$TMP/repo/." "$APP_DIR/"
  fi
  rm -rf "$TMP"
fi
mkdir -p "$APP_DIR/productions" "$APP_DIR/assets/music" "$APP_DIR/assets/ambience" "$APP_DIR/assets/sfx"

echo "▶ Environnement Python"
python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --upgrade pip wheel >/dev/null
"$APP_DIR/.venv/bin/pip" install "$APP_DIR[edge]"

if [ ! -f "$APP_DIR/.env" ]; then
  cp "$APP_DIR/.env.example" "$APP_DIR/.env"
  sed -i "s#^CHRONO_WORKDIR=.*#CHRONO_WORKDIR=$APP_DIR/productions#; s#^CHRONO_ASSETS_DIR=.*#CHRONO_ASSETS_DIR=$APP_DIR/assets#" "$APP_DIR/.env"
  echo "⚠  Remplissez $APP_DIR/.env (clés API, Telegram) avant de démarrer les services."
fi
chown -R chronoshorts:chronoshorts "$APP_DIR"
chmod 600 "$APP_DIR/.env"

echo "▶ Services systemd"
cp "$APP_DIR/deploy/chronoshorts-bot.service" "$APP_DIR/deploy/chronoshorts-scheduler.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable chronoshorts-bot chronoshorts-scheduler

cat <<EOF

✅ Installation terminée.
   1. nano $APP_DIR/.env            # clés API + Telegram
   2. sudo -u chronoshorts $APP_DIR/.venv/bin/chronoshorts check
   3. systemctl start chronoshorts-bot chronoshorts-scheduler
   4. journalctl -fu chronoshorts-bot
   Test manuel : sudo -u chronoshorts $APP_DIR/.venv/bin/chronoshorts produce --seed "Bagdad abbasside"
EOF
