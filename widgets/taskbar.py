import gi
gi.require_versions({"Gtk": "3.0", "GdkPixbuf": "2.0", "Glace": "0.1"})

from fabric.utils import bulk_connect
from fabric.widgets.button import Button
from fabric.widgets.image import Image
from gi.repository import GdkPixbuf, Glace

from services.window_manager import WindowManagerService
from shared.widget_container import BoxWidget
from utils.icon_resolver import IconResolver


class TaskBarWidget(BoxWidget):
    """A widget to display the taskbar items."""

    def __init__(self, **kwargs):
        super().__init__(
            name="taskbar",
            **kwargs,
        )

        self.icon_resolver = IconResolver()
        self.window_manager = WindowManagerService()
        self._is_wayland = self.window_manager.is_wayland

        if self._is_wayland:
            self._setup_wayland_taskbar()
        else:
            self.window_manager.connect("windows-changed", self._refresh_x11_windows)
            self._refresh_x11_windows()

    def on_app_id(
        self, client: Glace.Client, client_image: Image, client_button: Button, *_
    ):
        client_image.set_from_pixbuf(
            self.icon_resolver.get_icon_pixbuf(
                client.get_app_id(), self.config.get("icon_size", 22)
            )
        )
        client_button.set_tooltip_text(
            client.get_title() if self.config.get("tooltip", True) else None
        )

    def on_client_added(self, _, client: Glace.Client):
        client_image = Image()

        client_button = Button(
            style_classes=["buttons-basic", "buttons-transition"],
            image=client_image,
            on_button_press_event=lambda _, event: client.activate(),
        )

        bulk_connect(
            client,
            {
                "notify::app-id": lambda *_: self.on_app_id(
                    client, client_image, client_button
                ),
                "notify::activated": lambda *_: client_button.add_style_class("active")
                if client.get_activated()
                else client_button.remove_style_class("active"),
                "close": lambda *_: self.remove(client_button),
            },
        )

        self.add(client_button)

    def _setup_wayland_taskbar(self) -> None:
        self._manager = Glace.Manager()
        self._manager.connect("client-added", self.on_client_added)

    def _refresh_x11_windows(self, *_):
        for child in list(self.get_children()):
            self.remove(child)

        windows = self.window_manager.get_windows()
        icon_size = self.config.get("icon_size", 22)

        for window in windows:
            icon_pixbuf = window.get("icon")
            if icon_pixbuf:
                try:
                    icon_pixbuf = icon_pixbuf.scale_simple(
                        icon_size,
                        icon_size,
                        GdkPixbuf.InterpType.BILINEAR,
                    )
                except Exception:
                    # Scale failure should not break rendering.
                    pass
            else:
                icon_pixbuf = self.icon_resolver.get_icon_pixbuf(
                    window.get("app_id", "x11"), icon_size
                )

            window_image = Image(pixbuf=icon_pixbuf)
            window_button = Button(
                style_classes=["buttons-basic", "buttons-transition"],
                image=window_image,
                tooltip_text=(
                    window.get("title") if self.config.get("tooltip", True) else None
                ),
                on_button_press_event=lambda *_, window_id=window["id"]: self.window_manager.activate_window(window_id),
            )

            if window.get("active"):
                window_button.add_style_class("active")

            self.add(window_button)
