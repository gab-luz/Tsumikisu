from __future__ import annotations

import logging
from pathlib import Path
from shutil import which

# Use standard logging to avoid fabric dependency for this standalone utility
try:
    from fabric.utils import logger
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

HALO_PLACEHOLDER = "{{HALO_COLOR}}"
HALO_DEFAULT = "#8aff4c"


def _get_template_path() -> Path:
    return Path(__file__).resolve().parents[1] / "configs" / "i3" / "tsumikisu.conf"


def _build_replacements(halo_color: str) -> dict[str, str]:
    root = Path(__file__).resolve().parents[1]
    return {
        "{{TSUMIKISU_DIR}}": root.as_posix(),
        "{{LAUNCHER_SCRIPT}}": (root / "scripts" / "tsumikisu-launcher.py").as_posix(),
        "{{HOTKEYS_SCRIPT}}": (root / "scripts" / "tsumikisu-hotkeys.sh").as_posix(),
        HALO_PLACEHOLDER: halo_color,
    }


def sync_i3_config(halo_color: str | None = None) -> bool:
    """Rewrite $HOME/.config/i3/config from the template using the halo color."""
    if which("i3") is None:
        logger.warning("[I3] i3 binary not found; skipping halo sync.")
        return False

    template = _get_template_path()
    if not template.exists():
        logger.error("[I3] Template %s missing; cannot update config", template)
        return False

    color = halo_color or HALO_DEFAULT
    replacements = _build_replacements(color)

    content = template.read_text()
    for key, value in replacements.items():
        content = content.replace(key, value)

    target = Path.home() / ".config" / "i3"
    target.mkdir(parents=True, exist_ok=True)
    config_file = target / "config"

    config_file.write_text(content)
    logger.info("[I3] Wrote new config with halo color %s", color)
    return True
