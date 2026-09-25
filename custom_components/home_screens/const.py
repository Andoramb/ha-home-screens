"""Constants for the Home Screens integration."""

DOMAIN = "home_screens"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_PORT = 3000
DEFAULT_SCAN_INTERVAL = 30

ATTR_SCREEN = "screen"
ATTR_PROFILE = "profile"
ATTR_MINUTES = "minutes"
ATTR_TYPE = "type"
ATTR_TITLE = "title"
ATTR_MESSAGE = "message"
ATTR_DURATION = "duration"
ATTR_WAKE = "wake"

SERVICE_ALERT = "alert"
SERVICE_CLEAR_ALERTS = "clear_alerts"
SERVICE_SLEEP_OVERRIDE = "sleep_override"
SERVICE_GOTO_SCREEN = "goto_screen"

DISPLAY_STATE_ACTIVE = "active"
DISPLAY_STATE_DIMMED = "dimmed"
DISPLAY_STATE_ASLEEP = "asleep"
