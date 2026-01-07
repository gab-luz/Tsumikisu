from __future__ import annotations

from typing import Sequence

from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.scrolledwindow import ScrolledWindow

from shared.popup import PopupWindow
from utils.widget_settings import BarConfig


class CheatsheetOverlay(PopupWindow):
    """A simple cheatsheet overlay describing the key bindings."""

    HOTKEY_GROUPS: Sequence[tuple[str, list[tuple[str, str]]]] = [
        (
            "Launcher",
            [
                ("Super + Space", "Toggle the Tsumikisu app launcher."),
                ("Alt + F1", "Show this cheatsheet again."),
            ],
        ),
        (
            "Workspaces & Windows",
            [
                ("Super + 1…9", "Jump to workspace 1‑9 (dual monitor aware)."),
                ("Super + Q", "Close the currently focused window."),
            ],
        ),
        (
            "Apps",
            [
                ("Super + C", "Launch Visual Studio Code."),
                ("Super + T", "Launch the bundled Kitty terminal."),
            ],
        ),
    ]

    def __init__(self, config: BarConfig):
        module_config = config.get("modules", {}).get("cheatsheet", {})

        content = self._build_layout()

        super().__init__(
            name="hotkeys",
            title="Cheatsheet",
            anchor=module_config.get("anchor", "center"),
            layer=module_config.get("layer", "top"),
            transition_type=module_config.get("transition_type", "crossfade"),
            transition_duration=module_config.get("transition_duration", 350),
            enable_inhibitor=True,
            child=content,
        )

    def _build_layout(self) -> Box:
        header = Label(
            label="Tsumikisu Hotkeys",
            style_classes=["cheatsheet-title"],
        )

        row = Box(
            orientation="h",
            spacing=16,
            style_classes=["cheatsheet-row"],
        )

        for group_title, entries in self.HOTKEY_GROUPS:
            group = Box(
                orientation="v",
                spacing=8,
                style_classes=["cheatsheet-group"],
            )
            group.add(
                Label(
                    label=group_title,
                    style_classes=["cheatsheet-group-title"],
                )
            )

            for key, description in entries:
                group.add(self._build_entry(key, description))

            row.add(group)

        scroll = ScrolledWindow(
            child=row,
            min_content_size=(900, 320),
            h_expand=True,
            v_expand=True,
        )

        container = Box(
            name="cheatsheet",
            orientation="v",
            spacing=22,
            children=[header, scroll],
        )
        return container

    def _build_entry(self, key: str, description: str) -> Box:
        entry = Box(
            orientation="h",
            spacing=12,
            style_classes=["cheatsheet-entry"],
        )

        key_label = Label(label=key, style_classes=["cheatsheet-key"])
        description_label = Label(
            label=description,
            style_classes=["cheatsheet-description"],
            hexpand=True,
        )

        entry.add(key_label)
        entry.add(description_label)
        return entry
