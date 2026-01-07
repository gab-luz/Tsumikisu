"""Window manager helpers that work both on Wayland and X11."""

import os
from typing import Any

import gi
from fabric.core.service import Signal
from fabric.utils import bulk_connect, logger

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib

from .base import SingletonService

try:
    gi.require_version("Wnck", "3.0")
except ValueError:
    Wnck = None
else:
    from gi.repository import Wnck


class WindowManagerService(SingletonService):
    """Provides workspace and window metadata for both Wayland and X11."""

    @Signal
    def windows_changed(self) -> None: ...

    @Signal
    def workspaces_changed(self) -> None: ...

    def __init__(self) -> None:
        super().__init__()

        self.display = Gdk.Display.get_default()
        self.is_wayland = bool(os.environ.get("WAYLAND_DISPLAY"))
        self.is_x11 = not self.is_wayland and bool(os.environ.get("DISPLAY"))
        self._wnck_screen = None

        if self.is_x11:
            if Wnck is None:
                logger.warning(
                    "[WindowManager] Wnck is not available; X11 fallbacks will be disabled."
                )
                self.is_x11 = False
            else:
                self._wnck_screen = Wnck.Screen.get_default()
                GLib.idle_add(self._initialize_x11_watchers)

    def _initialize_x11_watchers(self) -> bool:
        if self._wnck_screen is None:
            return False

        self._wnck_screen.force_update()
        bulk_connect(
            self._wnck_screen,
            {
                "active-workspace-changed": self._notify_workspaces_changed,
                "workspace-added": self._notify_workspaces_changed,
                "workspace-removed": self._notify_workspaces_changed,
                "window-opened": self._notify_windows_changed,
                "window-closed": self._notify_windows_changed,
                "window-marked-urgent": self._notify_windows_changed,
                "window-unmarked-urgent": self._notify_windows_changed,
            },
        )

        self.emit("workspaces-changed")
        self.emit("windows-changed")
        return False

    def _notify_windows_changed(self, *_: Any) -> None:
        self.emit("windows-changed")

    def _notify_workspaces_changed(self, *_: Any) -> None:
        self.emit("workspaces-changed")

    def _wnck_ready(self) -> bool:
        return self._wnck_screen is not None

    def get_workspaces(self) -> list[dict[str, Any]]:
        """Return available workspaces for X11 sessions."""

        if not self._wnck_ready():
            return []

        self._wnck_screen.force_update()
        workspaces = []
        for workspace in self._wnck_screen.get_workspaces():
            workspace_id = workspace.get_number() + 1
            workspaces.append(
                {
                    "id": workspace_id,
                    "name": workspace.get_name() or str(workspace_id),
                    "occupied": workspace.get_window_count() > 0,
                    "active": workspace.is_active(),
                }
            )
        return workspaces

    def get_windows(self) -> list[dict[str, Any]]:
        """Return a list of visible X11 windows for the taskbar."""

        if not self._wnck_ready():
            return []

        self._wnck_screen.force_update()
        windows = []
        for window in self._wnck_screen.get_windows():
            if window.is_skip_tasklist():
                continue

            workspace = window.get_workspace()
            workspace_id = workspace.get_number() + 1 if workspace else None
            windows.append(
                {
                    "id": int(window.get_xid()),
                    "title": window.get_name() or "",
                    "app_id":
                    window.get_class_group_name()
                    or window.get_wm_class()
                    or "x11",
                    "active": window.is_active(),
                    "workspace": workspace_id,
                    "icon": window.get_icon(),
                    "window": window,
                }
            )
        return windows

    def activate_workspace(self, workspace_id: int) -> None:
        """Activate a workspace by its numeric identifier."""

        if not self._wnck_ready():
            return

        for workspace in self._wnck_screen.get_workspaces():
            if workspace.get_number() + 1 == workspace_id:
                workspace.activate(Gdk.CURRENT_TIME)
                self.emit("workspaces-changed")
                return

    def activate_window(self, window_id: int) -> None:
        """Activate a window referenced by its XID."""

        if not self._wnck_ready():
            return

        for window in self._wnck_screen.get_windows():
            if int(window.get_xid()) == window_id:
                window.activate(Gdk.CURRENT_TIME)
                self.emit("windows-changed")
                return
