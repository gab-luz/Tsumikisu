<p align="center"><img src="assets/images/tsumiki.png" align="centre" width="420" height="360"/></p>
<h1 align="center"><img src="https://raw.githubusercontent.com/JaKooLit/Telegram-Animated-Emojis/refs/heads/main/Activity/Sparkles.webp"/ height=35> Tsumikisu <img src="https://raw.githubusercontent.com/JaKooLit/Telegram-Animated-Emojis/refs/heads/main/Activity/Sparkles.webp"/ height=35></h1>
Tsumikisu (formerly Tsumiki / Hydepanel) started as a Hyprland-focused shell built on the [Fabric Widget System](https://github.com/Fabric-Development/fabric). Today this fork is taking a different path: it is being rebuilt as a pure **X11 shell** that tries to mimic the polish of Hyprland while avoiding the hard constraints of Wayland. The project is still in **pre-alpha**; much of the infrastructure is being reimagined so Tsumikisu can land on i3, sway-like layouts, or any other X11 session with confidence.

The name Tsumikisu blends “tsumiki” with “X11” (pronounced “su-me-ki-sue”), reminding you that this version is engineered for the Xorg layer while keeping the modular, lightweight spirit of the original building-block design.

> *No, this isn't Waybar. Yes, it's written in Python. Yes, it's still fast.* 🐍

> **Why X11?**  
I wanted a Hyprland-style desktop experience but the Wayland ecosystem kept getting in the way. Running the Android emulator was unreliable, Winboat never behaved under Wayland, DaVinci Resolve kept breaking, and every other graphical pipeline seemed to surface a new blocker. I expect many of those pain points may never be fixed or will take years to stabilize, so Tsumiki is being reborn on X11 where those problems either disappear or are much easier to work around.

> This repo is not yet ready for anyone who is not willing to help; features are incomplete, the dock/overview are brittle, and the overall experience is still pre-alpha. Use it only if you are curious about an X11-native Hyprland alternative and are happy to debug yourself.

<h2><sub><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Camera%20with%20Flash.png" alt="Camera with Flash" width="25" height="25" /></sub> Screenshots</h2>

<table align="center">
  <tr>
    <td colspan="4"><img src="assets/screenshots/main.png"></td>
  </tr>
    <tr>
    <td colspan="4"><img src="assets/screenshots/notification_menu.png"></td>
  </tr>
  <tr>
    <td colspan="1"><img src="assets/screenshots/quick_settings.png"></td>
    <td colspan="1"><img src="assets/screenshots/notifications.png"></td>
    <td colspan="1" align="center"><img src="assets/screenshots/logout.png"></td>
    <td colspan="1" align="center"><img src="assets/screenshots/weather.png"></td>
  </tr>
</table>

---

## ✨ Features

- 🖥 **Tailored for X11 Hyprland-style pipes**
  Inspired by Hyprland but architected to plug into i3/X11 sessions instead of a Wayland compositor.

- 🧩 **Modular Widget System**
  Includes pluggable widgets for Dock, Launcher, CPU, memory, network, media playback, battery, and more.

- 🎨 **Fully Themeable**
  Customize fonts, colors, layouts, and behavior using the power of Fabric.

- 🎨 **Material You Theming**
  Generate dynamic color schemes from your wallpaper using [Matugen](https://github.com/InioX/matugen). Configure in `theme.json` to automatically extract colors and apply Material You design.

- ⚙️ **Highly Configurable**
  Control the positioning, behavior, and appearance of every widget and element. Tailor the experience to fit your exact needs.

- 🔄 **Auto-Reload**
  Automatically restarts when configuration files are modified, making development and customization seamless.

- ⚡ **Lightweight & Fast**
  Designed with performance in mind — minimal memory and CPU usage.

- 📢 **On-Screen Display (OSD) Support**
  Display real-time notifications or alerts directly on the screen (e.g., for volume, media, or custom events) in a visually appealing overlay.

- 🛎️ **Notification System**
  Integrated notification support allows the panel to show alerts from your system, apps, or scripts. Notifications can be styled, timed, and customized based on user preferences.


## Prerequisites

- [JetBrains Nerd Font](https://www.nerdfonts.com)
- [python 3+](https://www.python.org/downloads/)

---

> [!NOTE]
> You need a functioning X11 session (i3, bspwm, etc.). Wayland compositors are not supported yet.

## **Getting Started**

### Required

Most of these are already installed on existing working machines

```sh
## network
networkmanager

## Sound
pipewire

## Bluetooth menu utilities
gnome-bluetooth-3.0 # aur
bluez
bluez-utils

## Compiler for sass/scss
dart-sass

## Brightness module for OSD
brightnessctl

## To open and execute commands in a terminal ex: updates, cava

kitty
```

### Optional

```sh

## To generate Material You color schemes from wallpaper
matugen

## To check for updates using the default pacman script in the updates module
pacman-contrib

## To display cava audio visualizer
cava

## To switch between power profiles in the battery module
power-profiles-daemon

## To record screen through recorder module
wf-recorder & slurp

## To adjust color temperature
redshift

## To keep the screen awake/inhibit when needed
xss-lock

## To use media module on quick settings
playerctl

## To use the clipboard module
cliphist

## To use the gpu module
nvtop

```

Clone this repository:

```sh
git clone https://github.com/rubiin/Tsumiki.git ~/.config/tsumikisu
```

- Run the following command to install the required packages for particular os, few of them are already installed if you have a working system:

## Installation

You can choose one of two installation methods: **Automated Setup** or **Manual Setup**.

### Option 1: Automated Setup Using `init.sh -setup`

1.  **Run the `init.sh -setup` script** to automatically setup the virtual environment and install all the required packages and dependencies (both `pacman` and AUR packages):

```sh
./init.sh -setup
```

This script will:

- Install all required `pacman` and AUR packages.
- Set up the virtual environment and any required configurations.

1.  **Start the environment or bar** once the installation is complete:

```sh
./init.sh -start
```

This will launch the environment or bar as defined in your project.

### Option 2: Manual Setup (Install Dependencies First)

If you prefer to have more control over the installation process, you can install the required dependencies manually and then run the `init.sh -start` script.

#### Step 1: Install pacman and AUR Packages

Using `yay` to install the required packages:

```sh
yay -S --needed	pipewire playerctl dart-sass power-profiles-daemon networkmanager brightnessctl pkgconf wf-recorder kitty python pacman-contrib gtk3 cairo gtk-layer-shell libgirepository noto-fonts-emoji gobject-introspection gobject-introspection-runtime libnotify cliphist satty nvtop gnome-bluetooth-3.0 slurp imagemagick tesseract tesseract-data-eng ttf-jetbrains-mono-nerd grimblast-git glace-git matugen-bin i3 i3status i3lock dmenu rofi xorg-server xorg-xinit xorg-xrandr xorg-xsetroot picom
```

If you have something else besides `yay`, install with the respective aur helper.

#### Step 2: Install Python Dependencies

You can install the required Python libraries either inside a virtual environment (recommended) or system-wide.

##### Using a Virtual Environment (Recommended)
It is highly recommended to use a virtual environment to avoid potential dependency conflicts.

First, create the virtual environment:
```sh
python3 -m venv .venv
```

Next, activate it:
```sh
source .venv/bin/activate
```
If you are a fish user, use `source .venv/bin/activate.fish`.

Finally, install the dependencies from requirements.txt:

```sh
pip install -r requirements.txt
```

##### Using the Package Manager (System-wide)
If you prefer a system-wide installation, you can use pacman to install the Python packages:
```sh
sudo pacman -S --needed python-pip python-gobject python-psutil python-cairo python-loguru python-requests python-fabric-git python-rlottie-python python-pytomlpp python-ijson
```

#### Step 3: Run the `init.sh -start` Script

Once the dependencies are installed, run the following command to start the bar or environment:

```sh
./init.sh -start
```

## **Usage**

On X11, add an exec line to your window manager or login script so Tsumikisu starts automatically.

```sh
exec --no-startup-id bash -c "sleep 3 && ~/.config/tsumikisu/init.sh -start"
```

Adjust the path if you keep the repo elsewhere.

### i3 integration and shortcuts

Running `./init.sh -setup` on a system with `i3` now writes `~/.config/i3/tsumikisu.conf` (based on `configs/i3/tsumikisu.conf`) and injects an `include` into `~/.config/i3/config` so the shell autostarts with your workspace manager. The snippet pins workspaces 1‑9 to `$primary_output`/`$secondary_output` (adjust those names with `xrandr`) to keep the layout sane on dual‑monitor rigs.

Keybindings provided by the template:

| Shortcut | Action |
| --- | --- |
| `Super + Space` | Toggles the built‑in App Launcher via `scripts/tsumikisu-launcher.py`, which calls the D‑Bus `toggle-window` action on the running shell. |
| `Super + Q` | Kills the currently focused window. |
| `Super + 1…9` | Switches to workspaces 1‑9 while respecting the output assignments. |
| `Super + C` | Launches Visual Studio Code. |
| `Super + T` | Launches the Kitty terminal the shell already ships with. |
| `Alt + F1` | Runs `scripts/tsumikisu-hotkeys.sh`, which now toggles the Fabric-powered cheatsheet overlay that lists these shortcuts. |

If you keep your repo somewhere other than `~/.config/tsumikisu`, edit the template at `configs/i3/tsumikisu.conf` so `$tsumikisu_dir`, `$launcher_cmd`, and `$hotkeys_cmd` point at your install location. After that the installer will keep replacing the snippet with the correct paths whenever you re-run `init.sh -setup`.

The cheatsheet overlay is powered by `modules.cheatsheet`; make sure that module is enabled in your config (the example config already sets `"modules":{"cheatsheet":{"enabled":true}}`) so `Alt + F1` always finds an active window to toggle.

## Updating

Updating to latest commit is fairly simple, just git pull the latest changes.

> **Note**: make sure to keep the config safe just in case

## Check [wiki](https://github.com/rubiin/Tsumiki/wiki) for configuring individual widgets

## **Available Modules**

| **Item**              | **Description**                                                                |
| --------------------- | ------------------------------------------------------------------------------ |
| **battery**           | Widget that display battery status and usage information.                      |
| **bluetooth**         | Widget manages Bluetooth connections and settings.                             |
| **brightness**        | Widget controls the screen brightness level.                                   |
| **cava**              | An audio visualizer widget.                                                    |
| **click_counter**     | Widget tracks the number of mouse clicks.                                      |
| **cliphist**          | Widget for the clipboard history.                                              |
| **custom_button_group** | Widget that defines a group of customizable buttons for executing shell commands. Buttons are not displayed as a group but can be individually placed anywhere in the layout using `@custom_button:0`, `@custom_button:1`, etc. Each button can have custom icons, labels, tooltips, and execute different commands when clicked. |
| **cpu**               | Widget displays CPU usage and performance statistics.                          |
| **date_time**         | A menu displaying the current date and notifications.                          |
| **divider (utility)** | Widget separates sections in a user interface for better organization.         |
| **emoji_picker**      | Widget that allows users to select and insert emojis.                          |
| **hypridle**         | Widget that tracks idle time or status of the system.                          |
| **hyprpicker**       | Widget that picks color from images.                                           |
| **hyprsunset**       | Widget that adjusts screen settings based on the time of sunset.               |
| **keyboard**          | Widget that manages and manages the keyboard layout or settings.               |
| **window_count**      | Widget that shows window count on active workspace.                            |
| **language**          | Widget allows selection of the system's language or locale settings.           |
| **media**             | Widget controls media playback, volume, or other media-related settings.       |
| **microphone**        | Widget manages microphone settings and input levels.                           |
| **network_usage**     | Widget displays the upload/download speeds.                                    |
| **ocr**               | Widget scans text from an image.                                               |
| **overview**          | Widget displays running applications in workspaces.                            |
| **power**             | Widget controls power-related settings, including sleep and shutdown.          |
| **ram**               | Widget displays information about system RAM usage and performance.            |
| **recorder**          | Widget for recording video on the system.                                      |
| **screenshot**       | Widget for taking screenshot on the system.                                    |
| **spacer (utility)**  | A simple utility for adding space in UI layouts.                               |
| **storage**           | Widget that displays storage usage and manages disk partitions or drives.      |
| **submap**            | Widget that displays active submap for hyprland.                               |
| **stopwatch**        | A utility for tracking elapsed time, like a timer or stopwatch.                |
| **system_tray**       | Widget that displays system tray icons and manages notifications.              |
| **taskbar**           | A bar at the bottom of the screen for quick access to apps and notifications.  |
| **updates**           | Widget that manages system updates, patches, and version upgrades.             |
| **quick_settings**    | Displays panel for quickly accessing some settings like brightness, sound etc. |
| **volume**            | Widget that controls the system’s audio volume.                                |
| **weather**           | Widget that displays current weather information or forecasts. Supports multiple weather providers (Open-Meteo and wttr.in) with provider switching and location-based cache invalidation.                 |
| **window_title**      | Widget that shows the title of the current window or application.              |
| **workspaces**        | Widget that displays virtual desktops or workspaces.                           |
| **world_clock**       | Widget that displays clock for various timezones.                              |

> [!WARNING]
> This is still in early development and will include breaking changes

## Frequently Asked Questions (FAQ)

### 1. **Cannot see system tray?**

Be sure to kill any bars that you may be running. You can kill other bar with `pkill bar-name`

### 2. **Cannot see notifications?**

Be sure to kill other notifications daemon that you may be running. You can kill other daemons with `pkill -f "mako|dunst|waybar"`

### 3. **Cannot see bar?**

Kill the app with `pkill tsumiki`. Run `init.sh -start`. This should show some logs. If it shows like `ModuleNotFoundError`, run `pip install -r requirements.txt`. If this does not solve the issue, do report a bug with screenshot of the log.

### 4. **Sass compilation error or UI not rendering?**
Your `theme.json` may be incorrect or outdated. You can copy the latest `theme.json` from the `example/` directory. Be aware that this will overwrite any custom changes you've made.


### 5. **No Icons?**
Make sure your icon theme has the required icons. One of the recommended icon theme is  `Tela Circle`


### 6. **ImportError: cannot import XX**
This error usually occurs when the required module/package is not installed or cannot be found. Make sure you have all the necessary dependencies installed. You can run
```sh
./init.sh -install
```
to install all the required packages and dependencies. Additionally, you can also manually install the package. Follow the instructions in the [Installation](#installation) section.



## Post-Installation

For X11 sessions you can start Tsumikisu from your `.xprofile`, `.xinitrc`, or i3 config, and pair it with a compositor of your choice (picom, xcompmgr, etc.). Example for `~/.xinitrc`:

```sh
# Tsumikisu shell
~/.config/tsumikisu/init.sh -start &
```

If you run on i3, the exec command above can live in `~/.config/i3/config` instead.

## Contributing

We welcome all sorts of contributions, no matter how small, to this project! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute.
