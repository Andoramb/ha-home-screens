"""Screen and profile selectors for Home Screens."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import HomeScreensApiError
from .const import DOMAIN
from .coordinator import HomeScreensCoordinator
from .entity import HomeScreensEntity

NO_PROFILE = "none"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: HomeScreensCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HomeScreensScreenSelect(coordinator), HomeScreensProfileSelect(coordinator)])


class HomeScreensScreenSelect(HomeScreensEntity, SelectEntity):
    """Jump to a screen by name (POST /api/display/goto-screen)."""

    _attr_translation_key = "screen"
    _attr_icon = "mdi:view-carousel"

    def __init__(self, coordinator: HomeScreensCoordinator) -> None:
        super().__init__(coordinator, "screen")

    @property
    def options(self) -> list[str]:
        return [s["name"] for s in (self.coordinator.data or {}).get("screens", []) if s.get("name")]

    @property
    def current_option(self) -> str | None:
        current = self._status.get("currentScreen") or {}
        return current.get("name")

    async def async_select_option(self, option: str) -> None:
        try:
            await self.coordinator.client.goto_screen(option)
        except HomeScreensApiError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()


class HomeScreensProfileSelect(HomeScreensEntity, SelectEntity):
    """Switch active profile (POST /api/display/profile). 'none' = show everything."""

    _attr_translation_key = "profile"
    _attr_icon = "mdi:account-cog"

    def __init__(self, coordinator: HomeScreensCoordinator) -> None:
        super().__init__(coordinator, "profile")

    @property
    def options(self) -> list[str]:
        names = [p["name"] for p in (self.coordinator.data or {}).get("profiles", []) if p.get("name")]
        return [NO_PROFILE, *names]

    @property
    def current_option(self) -> str | None:
        active = self._status.get("activeProfile")
        if not active:
            return NO_PROFILE
        for profile in (self.coordinator.data or {}).get("profiles", []):
            if profile.get("id") == active:
                return profile.get("name")
        return NO_PROFILE

    async def async_select_option(self, option: str) -> None:
        profile_id = ""
        if option != NO_PROFILE:
            for profile in (self.coordinator.data or {}).get("profiles", []):
                if profile.get("name") == option:
                    profile_id = profile["id"]
                    break
            else:
                raise HomeAssistantError(f"Unknown profile: {option}")
        try:
            await self.coordinator.client.set_profile(profile_id)
        except HomeScreensApiError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()
