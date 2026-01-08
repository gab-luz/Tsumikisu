import os

from fabric.core.widgets import WorkspaceButton
from fabric.utils import bulk_connect
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.label import Label

try:
    from fabric.hyprland.widgets import HyprlandWorkspaces as _HyprlandWorkspaces
except ImportError:  # pragma: no cover - optional dependency
    _HyprlandWorkspaces = None

from services.window_manager import WindowManagerService

from shared.widget_container import BoxWidget
from utils.functions import get_distro_icon, unique_list
from utils.widget_utils import nerd_font_icon


class WorkSpacesWidget(BoxWidget):
    """A widget to display the current workspaces."""

    def __init__(self, **kwargs):
        super().__init__(name="workspaces", spacing=1, **kwargs)

        config = self.config
        self.ignored_ws = {int(x) for x in unique_list(config.get("ignored", []))}
        self.icon_map = config.get("icon_map", {})
        self.default_format = config.get("default_label_format", "{id}")
        self.workspace_count = config.get("count", 8)
        self.hide_unoccupied = config.get("hide_unoccupied", False)
        self.show_numbered = config.get("show_numbered", True)

        self.icon = nerd_font_icon(
            icon=get_distro_icon(),
            props={"style_classes": ["panel-font-icon"]},
        )

        self.window_manager = WindowManagerService()
        hyprland_enabled = bool(os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"))
        self._use_hyprland_widget = (
            bool(self.window_manager.is_wayland)
            and hyprland_enabled
            and _HyprlandWorkspaces is not None
        )

        if self._use_hyprland_widget:
            self.workspace = _HyprlandWorkspaces(
                name="workspaces_widget",
                spacing=4,
                buttons=None
                if self.hide_unoccupied
                else [
                    self._setup_button(ws_id)
                    for ws_id in range(1, self.workspace_count + 1)
                    if ws_id not in self.ignored_ws
                ],
                buttons_factory=self._setup_button,
                invert_scroll=self.config.get("reverse_scroll", False),
                empty_scroll=self.config.get("empty_scroll", False),
            )

            self.children = (self.icon, self.workspace)
        else:
            self.workspace_box = Box(
                name="workspaces_box",
                spacing=4,
                style_classes=["workspace-button-group"],
                orientation="horizontal",
            )
            self.children = (self.icon, self.workspace_box)
            self.window_manager.connect(
                "workspaces-changed", lambda *_: self._refresh_x11_workspaces()
            )
            self._refresh_x11_workspaces()

    def _create_workspace_label(self, ws_id: int) -> str:
        return self.icon_map.get(str(ws_id), self.default_format.format(id=ws_id))

    def _update_empty_state(self, button: WorkspaceButton, *_):
        style_context = button.get_style_context()
        has_unoccupied = style_context.has_class("unoccupied")
        has_occupied = style_context.has_class("occupied")

        if button.empty:
            if not has_unoccupied:
                button.add_style_class("unoccupied")
            if has_occupied:
                button.remove_style_class("occupied")
        else:
            if has_unoccupied:
                button.remove_style_class("unoccupied")
            if not has_occupied:
                button.add_style_class("occupied")

    def _refresh_x11_workspaces(self) -> None:
        """Rebuild workspace buttons when running on X11."""

        if self._use_hyprland_widget:
            return

        for child in list(self.workspace_box.get_children()):
            self.workspace_box.remove(child)

        workspaces = [
            ws
            for ws in self.window_manager.get_workspaces()
            if ws["id"] not in self.ignored_ws
            and ws["id"] <= self.workspace_count
            and (not self.hide_unoccupied or ws["occupied"])
        ]

        for workspace in workspaces:
            label_text = self._create_workspace_label(
                workspace["id"]
            ) if self.show_numbered else None
            button = Button(
                style_classes=["workspace-button"],
                on_button_press_event=lambda *_, ws_id=workspace["id"]: self.window_manager.activate_workspace(ws_id),
            )
            if label_text:
                indicator = Label(
                    label=label_text,
                    style_classes=["workspace-number"],
                )
                button.add(indicator)
            self._apply_x11_workspace_style(button, workspace)
            self.workspace_box.add(button)

        self.workspace_box.show_all()

    def _apply_x11_workspace_style(self, button: Button, workspace: dict) -> None:
        if workspace.get("active"):
            button.add_style_class("active")
        else:
            button.remove_style_class("active")

        if workspace.get("occupied"):
            button.add_style_class("occupied")
            button.remove_style_class("unoccupied")
        else:
            button.add_style_class("unoccupied")
            button.remove_style_class("occupied")

    def _setup_button(self, ws_id: int) -> WorkspaceButton:
        button = WorkspaceButton(
            id=ws_id,
            label=None,
            visible=ws_id not in self.ignored_ws,
        )

        if self.show_numbered:
            label_text = self._create_workspace_label(ws_id)
            indicator = Label(
                label=label_text,
                style_classes=["workspace-number"],
            )
            button.add(indicator)

        # Only add empty state styling when showing all workspaces
        if not self.hide_unoccupied:
            # Connect to state changes
            bulk_connect(
                button,
                {
                    "notify::empty": lambda *args: self._update_empty_state(
                        button, *args
                    ),
                    "notify::active": lambda *args: self._update_empty_state(
                        button, *args
                    ),
                },
            )
            self._update_empty_state(button)
        return button
