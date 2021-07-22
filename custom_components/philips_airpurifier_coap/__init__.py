"""Support for Philips AirPurifier with CoAP."""
from __future__ import annotations

import asyncio
from asyncio.tasks import Task
import logging
from typing import Any, Callable

from aioairctrl import CoAPClient
import voluptuous as vol

from homeassistant.const import CONF_HOST, CONF_ICON, CONF_NAME
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_MODEL,
    DATA_KEY_CLIENT,
    DATA_KEY_COORDINATOR,
    DEFAULT_ICON,
    DEFAULT_NAME,
    DOMAIN,
    MODEL_AC1214,
    MODEL_AC2729,
    MODEL_AC2889,
    MODEL_AC2939,
    MODEL_AC2958,
    MODEL_AC3033,
    MODEL_AC3059,
    MODEL_AC3829,
    MODEL_AC3858,
    MODEL_AC4236,
)
from .model import DeviceStatus

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.ensure_list,
            [
                vol.Schema(
                    {
                        vol.Required(CONF_HOST): cv.string,
                        vol.Required(CONF_MODEL): vol.In(
                            [
                                MODEL_AC1214,
                                MODEL_AC2729,
                                MODEL_AC2889,
                                MODEL_AC2939,
                                MODEL_AC2958,
                                MODEL_AC3033,
                                MODEL_AC3059,
                                MODEL_AC3829,
                                MODEL_AC3858,
                                MODEL_AC4236,
                            ]
                        ),
                        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                        vol.Optional(CONF_ICON, default=DEFAULT_ICON): cv.icon,
                    },
                )
            ],
        )
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = ["fan", "sensor"]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Philips AirPurifier integration."""
    hass.data[DOMAIN] = {}

    async def async_setup_air_purifier(conf: ConfigType):
        host = conf[CONF_HOST]

        _LOGGER.debug("Setting up %s integration with %s", DOMAIN, host)

        try:
            client = await CoAPClient.create(host)
        except Exception as ex:
            _LOGGER.warning(r"Failed to connect: %s", ex)
            raise ConfigEntryNotReady from ex

        coordinator = Coordinator(client)

        hass.data[DOMAIN][host] = {
            DATA_KEY_CLIENT: client,
            DATA_KEY_COORDINATOR: coordinator,
        }

        await coordinator.async_first_refresh()

        for platform in PLATFORMS:
            hass.async_create_task(
                discovery.async_load_platform(hass, platform, DOMAIN, conf, config)
            )

    tasks = [async_setup_air_purifier(conf) for conf in config[DOMAIN]]
    if tasks:
        await asyncio.wait(tasks)

    return True


class Coordinator:
    def __init__(self, client: CoAPClient) -> None:
        self.client = client

        # It's None before the first successful update.
        # Components should call async_first_refresh  to make sure the first
        # update was successful. Set type to just DeviceStatus to remove
        # annoying checks that status is not None when it was already checked
        # during setup.
        self.status: DeviceStatus = None  # type: ignore[assignment]

        self._listeners: list[CALLBACK_TYPE] = []
        self._task: Task | None = None

    async def async_first_refresh(self) -> None:
        try:
            self.status = await self.client.get_status()
        except Exception as ex:
            raise ConfigEntryNotReady from ex

    @callback
    def async_add_listener(self, update_callback: CALLBACK_TYPE) -> Callable[[], None]:
        """Listen for data updates."""
        start_observing = not self._listeners

        self._listeners.append(update_callback)

        if start_observing:
            self._start_observing()

        @callback
        def remove_listener() -> None:
            """Remove update listener."""
            self.async_remove_listener(update_callback)

        return remove_listener

    @callback
    def async_remove_listener(self, update_callback) -> None:
        """Remove data update."""
        self._listeners.remove(update_callback)

        if not self._listeners and self._task:
            self._task.cancel()
            self._task = None

    async def _async_observe_status(self) -> None:
        async for status in self.client.observe_status():
            _LOGGER.debug("Status update: %s", status)
            self.status = status
            for update_callback in self._listeners:
                update_callback()

    def _start_observing(self) -> None:
        """Schedule state observation."""
        if self._task:
            self._task.cancel()
            self._task = None
        self._task = asyncio.create_task(self._async_observe_status())


class PhilipsEntity(Entity):
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__()
        self.coordinator = coordinator

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self):
        return self.coordinator.status is not None

    @property
    def _device_status(self) -> dict[str, Any]:
        return self.coordinator.status

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(self.coordinator.async_add_listener(self._handle_coordinator_update))

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
