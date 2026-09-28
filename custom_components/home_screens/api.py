"""Thin async client for the Home Screens HTTP API."""
from __future__ import annotations

import re
from typing import Any

import aiohttp

_CONTROL_CHARS = re.compile(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]")


class HomeScreensApiError(Exception):
    """Raised when the Home Screens API returns an unexpected response."""


class HomeScreensClient:
    """Talks to a Home Screens instance's REST API.

    See https://homescreens.dev/docs/api for the upstream reference.
    """

    def __init__(self, session: aiohttp.ClientSession, host: str, port: int, token: str | None = None) -> None:
        self._session = session
        self._base = f"http://{host}:{port}"
        self._token = token

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    async def _get(self, path: str) -> Any:
        async with self._session.get(
            f"{self._base}{path}", headers=self._headers(), timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            if resp.status != 200:
                raise HomeScreensApiError(f"GET {path} -> {resp.status}")
            raw = await resp.read()
            return _loads(raw)

    async def _post(self, path: str, payload: dict | None = None) -> Any:
        async with self._session.post(
            f"{self._base}{path}",
            headers=self._headers(),
            json=payload or {},
            timeout=aiohttp.ClientTimeout(total=10),
        ) as resp:
            if resp.status != 200:
                raise HomeScreensApiError(f"POST {path} -> {resp.status}")
            if resp.content_type == "application/json":
                raw = await resp.read()
                return _loads(raw)
            return None

    # -- read-only -----------------------------------------------------

    async def status(self) -> dict:
        return await self._get("/api/display/status")

    async def config(self) -> dict:
        return await self._get("/api/config")

    async def plugins_installed(self) -> dict:
        return await self._get("/api/plugins/installed")

    async def auth_status(self) -> dict:
        return await self._get("/api/auth/status")

    # -- display control -------------------------------------------------

    async def set_brightness(self, value: int) -> None:
        await self._post("/api/display/brightness", {"value": value})

    async def wake(self) -> None:
        await self._post("/api/display/wake")

    async def sleep(self) -> None:
        await self._post("/api/display/sleep")

    async def sleep_override(self, minutes: int) -> None:
        await self._post("/api/display/sleep-override", {"minutes": minutes})

    async def next_screen(self) -> None:
        await self._post("/api/display/next-screen")

    async def prev_screen(self) -> None:
        await self._post("/api/display/prev-screen")

    async def goto_screen(self, screen: str) -> None:
        await self._post("/api/display/goto-screen", {"screen": screen})

    async def set_profile(self, profile: str) -> None:
        await self._post("/api/display/profile", {"profile": profile})

    async def alert(
        self,
        title: str,
        message: str,
        alert_type: str = "info",
        duration: int = 15000,
        wake: bool = True,
    ) -> None:
        await self._post(
            "/api/display/alert",
            {
                "type": alert_type,
                "title": title,
                "message": message,
                "duration": duration,
                "wake": wake,
            },
        )

    async def clear_alerts(self) -> None:
        await self._post("/api/display/clear-alerts")

    async def module_command(self, module: str, action: str) -> None:
        await self._post("/api/display/module-command", {"module": module, "action": action})

    # -- module show/hide ------------------------------------------------

    async def set_module_enabled(self, module_id: str, enabled: bool) -> None:
        """Show or hide one module via POST /api/display/module-enabled.

        Display-token authorized, atomic on the server, and requires no
        editor session — unlike the old PUT /api/config workaround. Needs a
        Home Screens nightly build that includes this verb (added upstream
        2026-09-25).
        """
        await self._post("/api/display/module-enabled", {"moduleId": module_id, "enabled": enabled})


def _loads(raw: bytes) -> Any:
    """Home Screens sometimes embeds stray control bytes in string fields."""
    import json

    return json.loads(_CONTROL_CHARS.sub(b"", raw))
