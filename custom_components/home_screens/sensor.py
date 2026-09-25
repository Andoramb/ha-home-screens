"""Read-only status sensors for Home Screens."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import HomeScreensCoordinator
from .entity import HomeScreensEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: HomeScreensCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HomeScreensDisplayStateSensor(coordinator), HomeScreensCurrentScreenSensor(coordinator)])


class HomeScreensDisplayStateSensor(HomeScreensEntity, SensorEntity):
    """active / dimmed / asleep."""

    _attr_translation_key = "display_state"
    _attr_icon = "mdi:monitor-eye"
    _attr_options = ["active", "dimmed", "asleep"]
    _attr_device_class = "enum"

    def __init__(self, coordinator: HomeScreensCoordinator) -> None:
        super().__init__(coordinator, "display_state")

    @property
    def native_value(self) -> str | None:
        return self._status.get("displayState")


class HomeScreensCurrentScreenSensor(HomeScreensEntity, SensorEntity):
    """Name of the currently shown screen."""

    _attr_translation_key = "current_screen"
    _attr_icon = "mdi:view-dashboard"

    def __init__(self, coordinator: HomeScreensCoordinator) -> None:
        super().__init__(coordinator, "current_screen")

    @property
    def native_value(self) -> str | None:
        current = self._status.get("currentScreen") or {}
        return current.get("name")
