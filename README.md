# Home Assistant integration for Home Screens

A custom integration that exposes a self-hosted [Home Screens](https://github.com/home-screens/home-screens)
display as native Home Assistant entities, so you can control it from
dashboards and drive it with Node-RED / HA automations.

Talks to the Home Screens REST API (`/api/display/*`, `/api/config`) — see
https://homescreens.dev/docs/api. Local polling, no cloud, no extra
dependencies.

## Entities

| Entity | Description |
|---|---|
| `light.<name>_display` | On/off = wake/sleep, brightness = display brightness (0-100 mapped to HA's 0-255) |
| `select.<name>_screen` | Jump to any screen by name |
| `select.<name>_profile` | Switch active profile (`none` = show everything) |
| `switch.<name>_<screen>_<module type>` | One per module instance across every screen — show/hide that widget. e.g. `switch.home_screens_cameras_weather` for the weather module on the "Cameras" screen. A title is appended only to disambiguate two modules of the same type on the same screen. |
| `button.<name>_next_screen` / `prev_screen` | Screen navigation |
| `button.<name>_clear_alerts` | Dismiss active alerts |
| `sensor.<name>_display_state` | `active` / `dimmed` / `asleep` |
| `sensor.<name>_current_screen` | Name of the screen currently shown |

## Services

- `home_screens.alert` — show an alert/message overlay (`title`, `message`, `type`, `duration`, `wake`)
- `home_screens.clear_alerts`
- `home_screens.sleep_override` — hold off the sleep/dim schedule for N minutes
- `home_screens.goto_screen` — jump to a screen by name or id

## Installation

### HACS (custom repository)

1. HACS → Integrations → ⋮ → Custom repositories
2. Add this repo URL, category "Integration"
3. Install "Home Screens", restart Home Assistant

### Manual

Copy `custom_components/home_screens` into your Home Assistant `config/custom_components/` directory and restart.

## Setup

Settings → Devices & Services → Add Integration → "Home Screens" → enter the
display's host/IP, port (default `3000`), and a name for the device (default
`Home Screens`). The name becomes the device name and prefixes every entity
— it no longer bakes the IP into entity IDs.

If the target instance has a password set (Settings → On your phone → "Ask
for a password" in Home Screens), a bearer token isn't yet wired into the
config flow, so authenticated instances aren't supported yet. Track this in
issues if you need it.

## Notes on module show/hide

Requires a Home Screens **nightly build** — `POST /api/display/module-enabled`
was added upstream on 2026-09-25 and isn't in a stable release yet. It shows
or hides a module by id with just the display token, atomically, with no
editor session required.

Before that endpoint existed, this integration did a read → flip → write of
the whole config document via `PUT /api/config` (which needs a full editor
session once a password is set, and races the editor's own autosave). That
path has been removed now that the dedicated verb exists.

## License

MIT
