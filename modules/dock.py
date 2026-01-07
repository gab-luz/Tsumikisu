import gi
from fabric.utils import logger, truncate
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.eventbox import EventBox
from fabric.widgets.image import Image
from fabric.widgets.revealer import Revealer
from fabric.widgets.separator import Separator
from fabric.widgets.x11 import X11Window as Window
from gi.repository import GdkPixbuf, Gtk

from modules.app_launcher import AppLauncher
from services.window_manager import WindowManagerService
from utils.app import AppUtils
from utils.config import widget_config
from utils.constants import PINNED_APPS_FILE
from utils.functions import read_json_file, write_json_file
from utils.icon_resolver import IconResolver
from utils.widget_settings import BarConfig

gi.require_versions({"GdkPixbuf": "2.0", "Gtk": "3.0"})

# DnD target for dock app reordering
DOCK_DND_TARGET = [Gtk.TargetEntry.new("dock-app", Gtk.TargetFlags.SAME_APP, 0)]


class MultiDotIndicator(Gtk.DrawingArea):
    """A dot indicator widget that can show multiple dots for grouped apps."""

    def __init__(self, count=1, size=5, spacing=3, orientation="vertical"):
        super().__init__(visible=True)
        self._count = count
        self._size = size
        self._spacing = spacing
        self._orientation = orientation
        self._update_size()
        self.connect("draw", self.on_draw)

    def _update_size(self):
        if self._orientation == "vertical":
            # Dots stacked vertically (for horizontal dock)
            width = self._size
            height = (self._size * self._count) + (self._spacing * (self._count - 1))
        else:
            # Dots side by side (for vertical dock)
            width = (self._size * self._count) + (self._spacing * (self._count - 1))
            height = self._size
        self.set_size_request(width, height)

    def set_count(self, count: int):
        self._count = max(1, min(count, 5))  # Limit to 5 dots max
        self._update_size()
        self.queue_draw()

    def on_draw(self, area, cr):
        alloc = self.get_allocation()
        radius = self._size / 2 - 1

        for i in range(self._count):
            if self._orientation == "vertical":
                cx = alloc.width / 2
                cy = radius + 1 + i * (self._size + self._spacing)
            else:
                cx = radius + 1 + i * (self._size + self._spacing)
                cy = alloc.height / 2

            cr.arc(cx, cy, radius, 0, 2 * 3.14)
            cr.set_source_rgb(1.0, 1.0, 1.0)  # white dot
            cr.fill()


class DotIndicator(Gtk.DrawingArea):
    """A simple dot indicator widget."""

    def __init__(self, size=5):
        super().__init__(
            visible=True,
        )
        self.set_size_request(size, size)
        self.connect("draw", self.on_draw)

    def on_draw(self, area, cr):
        alloc = self.get_allocation()
        radius = min(alloc.width, alloc.height) / 2 - 1
        cr.arc(alloc.width / 2, alloc.height / 2, radius, 0, 2 * 3.14)

        cr.set_source_rgb(1.0, 1.0, 1.0)  # white dot
        cr.fill()



class AppBar(Box):
    """A simple app bar widget for the dock."""

    __slots__ = (
        "app_identifiers",
        "app_launcher",
        "app_util",
        "config",
        "icon_resolver",
        "icon_size",
        "menu",
        "orientation",
        "pinned_apps",
        "pinned_apps_container",
        "running_container",
        "separator",
        "truncation_size",
        "window_manager",
        "_group_apps",
    )

    def on_launcher_clicked(self, *_):
        """Toggle the app launcher visibility."""
        if self.app_launcher is None:
            self.app_launcher = AppLauncher(widget_config)
        self.app_launcher.toggle()

    def _bake_button(self, **kwargs) -> Button:
        return Button(
            style_classes=["buttons-basic", "buttons-transition", "dock-button"],
            **kwargs,
        )

    def __init__(self, parent):
        self.app_util = AppUtils()
        self.app_identifiers = self.app_util.app_identifiers

        self.config = parent.config
        self.menu = None
        self.app_launcher = None
        self.icon_size = self.config.get("icon_size", 30)
        self.orientation = self.config.get("orientation", "horizontal")
        self._group_apps = self.config.get("group_apps", True)
        self.truncation_size = self.config.get("truncation_size", 20)
        self.icon_resolver = IconResolver()
        self.window_manager = WindowManagerService()

        is_vertical = self.orientation == "vertical"
        box_orientation = "vertical" if is_vertical else "horizontal"
        launcher_style = "margin-bottom: 8px;" if is_vertical else "margin-right: 8px;"

        launcher_button = Button(
            style=launcher_style,
            image=Image(
                icon_name="view-app-grid-symbolic",
                icon_size=self.icon_size,
            ),
            on_button_press_event=self.on_launcher_clicked,
        )

        super().__init__(
            spacing=10,
            orientation=box_orientation,
            name="dock-bar",
            style_classes=["window-basic", "sleek-border", f"dock-{self.orientation}"],
            children=[launcher_button],
        )

        self.pinned_apps = read_json_file(PINNED_APPS_FILE) or []
        pinned_align = "h_align" if is_vertical else "v_align"
        self.pinned_apps_container = Box(
            spacing=7, orientation=box_orientation, **{pinned_align: "center"}
        )
        self.add(self.pinned_apps_container)
        self.separator = Separator(
            orientation="horizontal" if is_vertical else "vertical", visible=False
        )
        self.add(self.separator)
        self.running_container = Box(spacing=7, orientation=box_orientation)
        self.add(self.running_container)

        self._pinned_app_buttons = {}
        self._populate_pinned_apps(self.pinned_apps)

        self.window_manager.connect("windows-changed", self._refresh_running_apps)
        self.window_manager.connect("workspaces-changed", self._refresh_running_apps)
        self._refresh_running_apps()

    def _populate_pinned_apps(self, apps: list[str]):
        for child in list(self.pinned_apps_container.get_children()):
            self.pinned_apps_container.remove(child)
            child.destroy()
        self._pinned_app_buttons.clear()

        for item in apps:
            self._add_pinned_app_button(item)

        self.separator.set_visible(len(self._pinned_app_buttons) > 0)

    def _add_pinned_app_button(self, app_id: str) -> bool:
        if app_id in self._pinned_app_buttons:
            return False

        app = self.app_util.find_app(app_id)
        if not app:
            return False

        btn = self._bake_button(
            name="pinned_app",
            tooltip_markup=app.display_name,
            image=Image(
                pixbuf=app.get_icon_pixbuf(self.icon_size),
                size=self.icon_size,
            ),
            on_clicked=lambda *_, app=app: app.launch(),
        )
        self._pinned_app_buttons[app_id] = btn
        self.pinned_apps_container.add(btn)
        return True

    def _remove_pinned_app_button(self, app_id: str) -> bool:
        btn = self._pinned_app_buttons.pop(app_id, None)
        if btn:
            self.pinned_apps_container.remove(btn)
            btn.destroy()
            return True
        return False

    def _check_if_pinned(self, app_id: str) -> bool:
        return app_id in self.pinned_apps

    def _pin_app(self, app_id: str):
        if not self._check_if_pinned(app_id):
            self.pinned_apps.append(app_id)
            self._add_pinned_app_button(app_id)
            self._save_pinned_apps()

    def _unpin_app(self, app_id: str):
        if self._check_if_pinned(app_id):
            self.pinned_apps.remove(app_id)
            self._remove_pinned_app_button(app_id)
            self._save_pinned_apps()

    def _save_pinned_apps(self):
        write_json_file(PINNED_APPS_FILE, self.pinned_apps)

    def _refresh_running_apps(self, *_):
        windows = self.window_manager.get_windows()
        groups: dict[str, dict[str, list[dict]]] = {}
        ignored = set(self.config.get("ignored_apps", []))

        for window in windows:
            app_id = window.get("app_id") or "x11"
            if app_id in ignored:
                continue
            key = app_id if self._group_apps else f"{app_id}-{window.get('id')}"
            if key not in groups:
                groups[key] = {"app_id": app_id, "windows": []}
            groups[key]["windows"].append(window)

        self._clear_running_container()
        for group in groups.values():
            self._create_app_group(group["app_id"], group["windows"])

    def _clear_running_container(self):
        for child in list(self.running_container.get_children()):
            self.running_container.remove(child)
            child.destroy()

    def _create_app_group(self, app_id: str, windows: list[dict]):
        is_vertical = self.orientation == "vertical"
        indicator_orientation = "vertical" if is_vertical else "horizontal"

        icon_pixbuf = self._resolve_group_icon(app_id, windows)
        client_image = Image(size=self.icon_size)
        if icon_pixbuf:
            client_image.set_from_pixbuf(icon_pixbuf)

        indicator = (
            MultiDotIndicator(
                count=len(windows),
                size=5,
                spacing=3,
                orientation=indicator_orientation,
            )
            if self._group_apps
            else DotIndicator(size=5)
        )

        tooltip = windows[0].get("title") if self.config.get("tooltip", True) else None
        client_button = self._bake_button(
            image=client_image,
            tooltip_text=tooltip,
            on_clicked=lambda *_: self._activate_next_window(windows),
        )

        if any(win.get("active") for win in windows):
            client_button.add_style_class("active")

        client_button.connect(
            "button-press-event",
            lambda widget, event, app_id=app_id, windows=windows: self._on_group_button_press(
                widget, event, app_id, windows
            ),
        )

        if is_vertical:
            box = Box(
                orientation="horizontal",
                spacing=0,
                h_align="center",
                children=[
                    Box(v_align="center", children=[indicator]),
                    client_button,
                ],
            )
        else:
            box = Box(
                orientation="vertical",
                spacing=4,
                v_align="center",
                children=[
                    client_button,
                    Box(h_align="center", children=[indicator]),
                ],
            )

        self.running_container.add(box)

    def _activate_next_window(self, windows: list[dict]):
        if not windows:
            return
        active_idx = next((i for i, win in enumerate(windows) if win.get("active")), -1)
        target = windows[(active_idx + 1) % len(windows)]
        self.window_manager.activate_window(target["id"])

    def _resolve_group_icon(self, app_id: str, windows: list[dict]):
        for window in windows:
            icon = window.get("icon")
            if icon:
                return self._scale_icon(icon)
        return self.icon_resolver.get_icon_pixbuf(app_id, self.icon_size)

    def _scale_icon(self, pixbuf):
        if pixbuf is None:
            return None
        try:
            return pixbuf.scale_simple(
                self.icon_size,
                self.icon_size,
                GdkPixbuf.InterpType.BILINEAR,
            )
        except Exception:
            logger.warning("[Dock] Failed to scale running app icon")
            return pixbuf

    def _on_group_button_press(self, widget, event, app_id: str, windows: list[dict]):
        if event.button == 3:
            self._show_group_menu(app_id, windows)
            self.menu.popup_at_pointer(event)
            return True
        return False

    def _show_group_menu(self, app_id: str, windows: list[dict]):
        self._init_menu()
        for window in windows:
            title = truncate(window.get("title") or app_id, self.truncation_size)
            item = Gtk.MenuItem(label=title)
            item.connect(
                "activate",
                lambda *_, window_id=window["id"]: self.window_manager.activate_window(
                    window_id
                ),
            )
            self.menu.add(item)

        self.menu.add(Gtk.SeparatorMenuItem())
        for item in self._build_common_menu_items(app_id, windows):
            self.menu.add(item)
        self.menu.show_all()

    def _build_common_menu_items(self, app_id: str, windows: list[dict]):
        items = []
        items.append(
            self._make_item(
                "Close All",
                lambda: [self._close_window(win) for win in windows.copy()],
            )
        )

        if self._check_if_pinned(app_id):
            items.append(self._make_item("Unpin", lambda: self._unpin_app(app_id)))
        else:
            items.append(self._make_item("Pin", lambda: self._pin_app(app_id)))

        app = self.app_util.find_app(app_id)
        if app:
            items.append(self._make_item("New Window", lambda: app.launch()))

        return items

    def _close_window(self, window: dict):
        win_obj = window.get("window")
        if win_obj:
            try:
                win_obj.close()
            except Exception:
                logger.exception("[Dock] Failed to close running window")

    def _make_item(self, label: str, callback):
        mi = Gtk.MenuItem(label=label)
        mi.connect("activate", lambda *_: callback())
        return mi

    def _init_menu(self):
        if not self.menu:
            self.menu = Gtk.Menu()
        else:
            for item in self.menu.get_children():
                self.menu.remove(item)
                item.destroy()


class Dock(Window):
    """A dock for applications."""

    def __init__(self, config: BarConfig):
        self.config = config.get("modules", {}).get("dock", {})
        self._app_bar = AppBar(self)

        # Determine orientation and set appropriate styles
        orientation = self.config.get("orientation", "horizontal")
        is_vertical = orientation == "vertical"

        # Set padding and transition based on orientation
        if is_vertical:
            padding_style = "padding: 50px 5px 50px 20px;"
            transition_type = "slide-right"
        else:
            padding_style = "padding: 20px 50px 5px 50px;"
            transition_type = "slide-up"

        self.revealer = Revealer(
            child=Box(children=[self._app_bar], style=padding_style),
            transition_duration=500,
            transition_type=transition_type,
        )

        if self.config.get("behavior", "always_show") == "always_show":
            self.revealer.set_reveal_child(True)
            child = self.revealer
        else:
            # Adjust CenterBox for vertical orientation
            if is_vertical:
                centerbox = CenterBox(
                    orientation="vertical",
                    center_children=self.revealer,
                    start_children=Box(style="min-height: 5px; min-width: 10px;"),
                    end_children=Box(style="min-height: 5px; min-width: 10px;"),
                )
            else:
                centerbox = CenterBox(
                    center_children=self.revealer,
                    start_children=Box(style="min-height: 10px; min-width: 5px;"),
                    end_children=Box(style="min-height: 10px; min-width: 5px;"),
                )

            child = EventBox(
                events=["enter-notify", "leave-notify"],
                child=centerbox,
                on_enter_notify_event=lambda *_: self.revealer.set_reveal_child(True),
                on_leave_notify_event=lambda *_: self._on_leave_notify(),
            )

        self.window_manager = self._app_bar.window_manager

        if (
            self.config.get("show_when_no_windows", False)
            and self.config.get("behavior", "always_hide") == "intellihide"
        ):
            self.window_manager.connect("windows-changed", self._check_for_windows)
            self.window_manager.connect("workspaces-changed", self._check_for_windows)
            self._check_for_windows()

        # Determine anchor based on config or default based on orientation
        default_anchor = "center-left" if is_vertical else "bottom-center"
        anchor = self.config.get("anchor", default_anchor)

        super().__init__(
            layer=self.config.get("layer", "top"),
            anchor=anchor,
            child=child,
            name="dock",
            title="dock",
        )

    def _on_leave_notify(self):
        """Hide the dock when the pointer leaves."""
        self.revealer.set_reveal_child(False)

    def _check_for_windows(self, *_):
        if self._active_workspace_has_windows():
            self.revealer.set_reveal_child(False)
        else:
            self.revealer.set_reveal_child(True)

    def _active_workspace_has_windows(self) -> bool:
        windows = self.window_manager.get_windows()
        if not windows:
            return False

        workspaces = self.window_manager.get_workspaces()
        active_workspace = next((ws for ws in workspaces if ws.get("active")), None)
        if active_workspace is None:
            return bool(windows)

        active_id = active_workspace.get("id")
        return any(win.get("workspace") == active_id for win in windows)
