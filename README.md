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
| `switch.<name>_<module>` | One per module instance across every screen — show/hide that widget |
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
display's host/IP and port (default `3000`).

If the target instance has a password set (Settings → On your phone → "Ask
for a password" in Home Screens), module show/hide (`PUT /api/config`)
requires a signed-in session rather than a display token and is not yet
supported by this integration — everything else (`/api/display/*`) works
with a bearer token, which is not yet wired into the config flow. Track
this in issues if you need it.

## Notes on module show/hide

Home Screens has no dedicated REST verb for toggling a module's visibility
— it's a `enabled` flag on the module instance inside the config document
(`PUT /api/config`). This integration does a safe read → flip → write using
the `X-Config-Revision` header as a compare-and-swap, so it won't clobber a
concurrent edit made in the Home Screens editor.

## License

MIT
