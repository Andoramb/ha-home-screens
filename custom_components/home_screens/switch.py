"""One switch per module instance, for show/hide (PUT /api/config)."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import HomeScreensApiError
from .const import DOMAIN
from .coordinator import HomeScreensCoordinator
from .entity import HomeScreensEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: HomeScreensCoordinator = hass.data[DOMAIN][entry.entry_id]
    known_ids: set[str] = set()

    @callback
    def _async_add_new_modules() -> None:
        new_entities = []
        for module in coordinator.modules():
            module_id = module["id"]
            if not module_id or module_id in known_ids:
                continue
            known_ids.add(module_id)
            new_entities.append(HomeScreensModuleSwitch(coordinator, module_id))
        if new_entities:
            async_add_entities(new_entities)

    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_modules))
    _async_add_new_modules()


class HomeScreensModuleSwitch(HomeScreensEntity, SwitchEntity):
    """Show/hide a single module instance (any module type)."""

    _attr_icon = "mdi:widgets"

    def __init__(self, coordinator: HomeScreensCoordinator, module_id: str) -> None:
        super().__init__(coordinator, f"module_{module_id}")
        self._module_id = module_id

    def _module(self) -> dict | None:
        for module in self.coordinator.modules():
            if module["id"] == self._module_id:
                return module
        return None

    @property
    def available(self) -> bool:
        return super().available and self._module() is not None

    @property
    def name(self) -> str:
        module = self._module()
        if module is None:
            return self._module_id
        label = module.get("title") or module.get("type") or self._module_id
        return f"{label} ({module.get('screen_name')})" if module.get("screen_name") else label

    @property
    def is_on(self) -> bool:
        module = self._module()
        return bool(module and module.get("enabled", True))

    async def async_turn_on(self, **kwargs) -> None:
        await self._async_set(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._async_set(False)

    async def _async_set(self, enabled: bool) -> None:
        try:
            await self.coordinator.client.set_module_enabled(self._module_id, enabled)
        except HomeScreensApiError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()
