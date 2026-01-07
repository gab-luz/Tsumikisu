#!/usr/bin/env sh
set -eu

if [ "$(id -u)" -ne 0 ]; then
  if command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
  else
    printf 'This script requires root privileges.\n'
    exit 1
  fi
else
  SUDO=""
fi

if [ -f /etc/os-release ]; then
  . /etc/os-release
else
  printf 'Unable to detect distribution from /etc/os-release.\n'
  exit 1
fi

case "$ID" in
debian|ubuntu)
  PKGS="
    python3
    python3-pip
    python3-venv
    python3-gi
    python3-gi-cairo
    gir1.2-gtk-3.0
    gir1.2-gdkpixbuf-2.0
    gir1.2-glib-2.0
    gir1.2-cairo-1.0
    pkg-config
    libgirepository1.0-dev
    libcairo2
    libpango-1.0-0
    libgdk-pixbuf2.0-0
    build-essential
    git
  "
  "$SUDO" apt-get update
  "$SUDO" apt-get install -y $PKGS
  ;;
arch)
  PKGS="
    python
    python-pip
    python-virtualenv
    python-gobject
    python-cairo
    gobject-introspection
    gtk3
    cairo
    pango
    gdk-pixbuf2
    pkgconf
    git
  "
  "$SUDO" pacman -Sy --noconfirm $(printf '%s ' $PKGS)
  ;;
*)
  printf 'Unsupported distribution: %s\n' "$ID"
  exit 1
  ;;
esac
# installing python packages
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install uv
python3 -m pip install -r requirements.txt

printf '\nAll dependencies installed (system and Python packages).\n'
