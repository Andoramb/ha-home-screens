"""The Home Screens integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HomeScreensApiError, HomeScreensClient
from .const import (
    ATTR_DURATION,
    ATTR_MESSAGE,
    ATTR_MINUTES,
    ATTR_SCREEN,
    ATTR_TITLE,
    ATTR_TYPE,
    ATTR_WAKE,
    CONF_HOST,
    CONF_PORT,
    DOMAIN,
    SERVICE_ALERT,
    SERVICE_CLEAR_ALERTS,
    SERVICE_GOTO_SCREEN,
    SERVICE_SLEEP_OVERRIDE,
)
from .coordinator import HomeScreensCoordinator

PLATFORMS = ["light", "select", "switch", "button", "sensor"]

ALERT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TITLE): cv.string,
        vol.Required(ATTR_MESSAGE): cv.string,
        vol.Optional(ATTR_TYPE, default="info"): vol.In(["info", "warning", "urgent"]),
        vol.Optional(ATTR_DURATION, default=15000): vol.All(int, vol.Range(min=0)),
        vol.Optional(ATTR_WAKE, default=True): cv.boolean,
    }
)
SLEEP_OVERRIDE_SCHEMA = vol.Schema({vol.Required(ATTR_MINUTES): vol.All(int, vol.Range(min=1, max=1440))})
GOTO_SCREEN_SCHEMA = vol.Schema({vol.Required(ATTR_SCREEN): cv.string})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    client = HomeScreensClient(session, entry.data[CONF_HOST], entry.data[CONF_PORT])
    coordinator = HomeScreensCoordinator(hass, entry, client)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:  # noqa: BLE001 - surfaced by HA as setup retry
        raise HomeAssistantError(f"Could not connect to Home Screens: {err}") from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    _async_register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            for service in (SERVICE_ALERT, SERVICE_CLEAR_ALERTS, SERVICE_SLEEP_OVERRIDE, SERVICE_GOTO_SCREEN):
                hass.services.async_remove(DOMAIN, service)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


def _async_register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_ALERT):
        return

    def _first_coordinator() -> HomeScreensCoordinator:
        return next(iter(hass.data[DOMAIN].values()))

    async def _async_alert(call: ServiceCall) -> None:
        client = _first_coordinator().client
        try:
            await client.alert(
                title=call.data[ATTR_TITLE],
                message=call.data[ATTR_MESSAGE],
                alert_type=call.data[ATTR_TYPE],
                duration=call.data[ATTR_DURATION],
                wake=call.data[ATTR_WAKE],
            )
        except HomeScreensApiError as err:
            raise HomeAssistantError(str(err)) from err

    async def _async_clear_alerts(call: ServiceCall) -> None:
        try:
            await _first_coordinator().client.clear_alerts()
        except HomeScreensApiError as err:
            raise HomeAssistantError(str(err)) from err

    async def _async_sleep_override(call: ServiceCall) -> None:
        try:
            await _first_coordinator().client.sleep_override(call.data[ATTR_MINUTES])
        except HomeScreensApiError as err:
            raise HomeAssistantError(str(err)) from err

    async def _async_goto_screen(call: ServiceCall) -> None:
        try:
            await _first_coordinator().client.goto_screen(call.data[ATTR_SCREEN])
        except HomeScreensApiError as err:
            raise HomeAssistantError(str(err)) from err
        await _first_coordinator().async_request_refresh()

    hass.services.async_register(DOMAIN, SERVICE_ALERT, _async_alert, schema=ALERT_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_CLEAR_ALERTS, _async_clear_alerts)
    hass.services.async_register(DOMAIN, SERVICE_SLEEP_OVERRIDE, _async_sleep_override, schema=SLEEP_OVERRIDE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_GOTO_SCREEN, _async_goto_screen, schema=GOTO_SCREEN_SCHEMA)
