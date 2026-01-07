#!/usr/bin/env python3
from __future__ import annotations

import sys

from gi.repository import Gio, GLib

APPLICATION_ID = "tsumiki"
BUS_NAME = f"org.gtk.Application.{APPLICATION_ID}"
OBJECT_PATH = f"/org/gtk/Application/{APPLICATION_ID}"
ACTION_NAME = "toggle-window"
DEFAULT_WINDOW = "launcher"


def toggle_window(window_name: str) -> None:
    try:
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        proxy = Gio.DBusProxy.new_sync(
            bus,
            Gio.DBusProxyFlags.NONE,
            None,
            BUS_NAME,
            OBJECT_PATH,
            "org.gtk.Application",
            None,
        )
        parameter = GLib.Variant("s", window_name)
        proxy.call_sync(
            "ActivateAction",
            GLib.Variant("(s v s)", (ACTION_NAME, parameter, "")),
            Gio.DBusCallFlags.NONE,
            -1,
            None,
        )
    except Exception as exc:  # pragma: no cover - user-facing shell script
        raise SystemExit(
            f"Unable to toggle '{window_name}': {exc}. Is Tsumikisu running?"
        )


def main() -> None:
    window_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_WINDOW
    toggle_window(window_name)


if __name__ == "__main__":
    main()
