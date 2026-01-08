from typing import ClassVar

import gi
from fabric.utils import bulk_connect, logger
from fabric.widgets.box import Box
from fabric.widgets.window import Window
from fabric.widgets.widget import Widget
from gi.repository import Gdk, GLib, GObject

from services.window_manager import WindowManagerService

gi.require_versions({"Gtk": "3.0", "Gdk": "3.0", "GObject": "2.0"})


class PopoverManager:
    """Singleton manager to handle shared resources for popovers."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        self._overlay = None
        self.active_popover = None
        self.available_windows = []
        self._window_manager = WindowManagerService()
        self._window_manager.connect("windows-changed", self._hide_active_popover)
        self._window_manager.connect("workspaces-changed", self._hide_active_popover)

    @property
    def overlay(self):
        """Lazily create the overlay window on first access."""
        if self._overlay is None:
            self._overlay = Window(
                name="popover-overlay",
                style_classes=["popover-overlay"],
                title="tsumiki",
                anchor="left top right bottom",
                exclusivity="normal",
                layer="overlay",
                visible=False,
            )
            self._overlay.add(Box())
            self._overlay.connect("button-press-event", self.on_overlay_clicked)
        return self._overlay

    def _hide_active_popover(self, *_):
        if self.active_popover:
            self.active_popover.hide_popover()

    def on_overlay_clicked(self, widget, event):
        if self.active_popover:
            self.active_popover.hide_popover()
        return True

    def get_popover_window(self):
        """Get an available popover window or create a new one."""
        if self.available_windows:
            return self.available_windows.pop()

        window = Window(
            type="popup",
            layer="overlay",
            name="popover-window",
            anchor="left top",
            visible=False,
        )
        window.set_keep_above(True)
        return window

    def return_popover_window(self, window):
        """Return a popover window to the pool."""
        for child in window.get_children():
            window.remove(child)
        window.hide()
        if len(self.available_windows) < 5:
            self.available_windows.append(window)
        else:
            window.destroy()

    def activate_popover(self, popover):
        """Set the active popover and show overlay."""
        if self.active_popover and self.active_popover != popover:
            self.active_popover.hide_popover()

        self.active_popover = popover
        self.overlay.show()


@GObject.Signal(
    flags=GObject.SignalFlags.RUN_LAST, return_type=GObject.TYPE_NONE, arg_types=()
)
def popover_opened(widget: Widget): ...


@GObject.Signal(
    flags=GObject.SignalFlags.RUN_LAST, return_type=GObject.TYPE_NONE, arg_types=()
)
def popover_closed(widget: Widget): ...


@GObject.type_register
class Popover(Widget):
    """Memory-efficient popover implementation."""

    __gsignals__: ClassVar = {
        "popover-opened": (GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE, ()),
        "popover-closed": (GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE, ()),
    }

    def __init__(
        self,
        point_to,
        content_factory=None,
        content=None,
    ):
        super().__init__()

        self._content_factory = content_factory
        self._point_to = point_to
        self._content_window = None
        self._content = content
        self._visible = False
        self._manager = PopoverManager()

    def set_content_factory(self, content_factory):
        self._content_factory = content_factory

    def set_content(self, content):
        self._content = content

    def set_pointing_to(self, widget):
        self._point_to = widget

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape and self._manager.active_popover:
            self._manager.active_popover.hide_popover()

    def open(self, *_):
        if not self._content_window:
            try:
                self._create_popover()
            except Exception as e:
                logger.exception(f"Could not create popover! Error: {e}")
                return
        else:
            self._manager.activate_popover(self)
            self._content_window.show()
            self._visible = True

        self.emit("popover-opened")

    def _calculate_margins(self):
        widget_allocation = self._point_to.get_allocation()
        popover_size = self._content_window.get_size()

        display = Gdk.Display.get_default()
        screen = display.get_default_screen()
        monitor_at_window = screen.get_monitor_at_window(
            self._point_to.get_window()
        )
        if monitor_at_window < 0:
            monitor_at_window = 0
        monitor_geometry = screen.get_monitor_geometry(monitor_at_window)

        x = (
            widget_allocation.x
            + (widget_allocation.width / 2)
            - (popover_size.width / 2)
        )
        y = widget_allocation.y - 5

        if x <= 0:
            x = widget_allocation.x
        elif x + popover_size.width >= monitor_geometry.width:
            x = widget_allocation.x - popover_size.width + widget_allocation.width

        return [y, 0, 0, x]

    def set_position(self, position: tuple[int, int, int, int] | None = None):
        if not self._content_window:
            return False

        margins = position if position is not None else self._calculate_margins()
        y, _, _, x = margins
        self._content_window.move(int(x), int(y))
        return False

    def on_content_ready(self, widget, event):
        self.set_position()

    def _create_popover(self):
        if self._content is None and self._content_factory is not None:
            self._content = self._content_factory()

        self._content_window = self._manager.get_popover_window()
        self._content.connect("draw", self.on_content_ready)

        self._content_window.add(Box(name="popover-content", children=self._content))

        bulk_connect(
            self._content_window,
            {
                "focus-out-event": self.on_popover_focus_out,
                "key-press-event": self.on_key_press,
            },
        )

        self._manager.activate_popover(self)
        self._content_window.show()
        self._visible = True

    def on_popover_focus_out(self, widget, event):
        GLib.timeout_add(100, self.hide_popover)
        return False

    def hide_popover(self):
        if not self._visible or not self._content_window:
            return False

        self._content_window.hide()
        self._manager.overlay.hide()
        self._visible = False
        self.emit("popover-closed")
        return False
