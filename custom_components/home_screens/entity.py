"""Base entity for the Home Screens integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HomeScreensCoordinator


class HomeScreensEntity(CoordinatorEntity[HomeScreensCoordinator]):
    """Common device_info / unique_id plumbing."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HomeScreensCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._key = key
        host = coordinator.entry.data["host"]
        self._attr_unique_id = f"{host}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        host = self.coordinator.entry.data["host"]
        port = self.coordinator.entry.data["port"]
        return DeviceInfo(
            identifiers={(DOMAIN, host)},
            name=self.coordinator.entry.title,
            manufacturer="home-screens",
            model="Home Screens display",
            configuration_url=f"http://{host}:{port}",
        )

    @property
    def _status(self) -> dict:
        return (self.coordinator.data or {}).get("status", {})
