"""Philips Air Purifier & Humidifier Sensors"""
from __future__ import annotations

import logging
from typing import Any, Callable, List, cast

from homeassistant.components.sensor import ATTR_STATE_CLASS, SensorEntity
from homeassistant.const import ATTR_DEVICE_CLASS, ATTR_ICON, CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, StateType

from . import Coordinator, PhilipsEntity
from .const import (
    ATTR_FILTER_ACTIVE_CARBON_REMAINING_RAW,
    ATTR_FILTER_ACTIVE_CARBON_TYPE,
    ATTR_FILTER_HEPA_REMAINING_RAW,
    ATTR_FILTER_HEPA_TYPE,
    ATTR_FILTER_PRE_REMAINING_RAW,
    ATTR_FILTER_WICK_REMAINING_RAW,
    ATTR_LABEL,
    ATTR_UNIT,
    ATTR_VALUE,
    CONF_MODEL,
    DATA_KEY_COORDINATOR,
    DOMAIN,
    PHILIPS_DEVICE_ID,
    PHILIPS_FILTER_ACTIVE_CARBON_REMAINING,
    PHILIPS_FILTER_ACTIVE_CARBON_TYPE,
    PHILIPS_FILTER_HEPA_REMAINING,
    PHILIPS_FILTER_HEPA_TYPE,
    PHILIPS_FILTER_PRE_REMAINING,
    PHILIPS_FILTER_WICK_REMAINING,
    SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: Callable[[List[Entity], bool], None],
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    if discovery_info is None:
        return

    host = discovery_info[CONF_HOST]
    model = discovery_info[CONF_MODEL]
    name = discovery_info[CONF_NAME]
    data = hass.data[DOMAIN][host]

    coordinator = data[DATA_KEY_COORDINATOR]

    sensors = []
    for sensor in SENSOR_TYPES:
        if coordinator.status.get(sensor):
            sensors.append(PhilipsSensor(coordinator, name, model, sensor))

    async_add_entities(sensors, update_before_add=False)


class PhilipsSensor(PhilipsEntity, SensorEntity):
    """Define a Philips AirPurifier sensor."""

    def __init__(self, coordinator: Coordinator, name: str, model: str, kind: str) -> None:
        super().__init__(coordinator)
        self._model = model
        self._description = SENSOR_TYPES[kind]
        self._attr_device_class = self._description.get(ATTR_DEVICE_CLASS)
        self._attr_icon = self._description.get(ATTR_ICON)
        self._attr_name = f"{name} {self._description[ATTR_LABEL].replace('_', ' ').title()}"
        self._attr_state_class = self._description.get(ATTR_STATE_CLASS)
        self._attr_unit_of_measurement = self._description.get(ATTR_UNIT)
        try:
            device_id = self._device_status[PHILIPS_DEVICE_ID]
            self._attr_unique_id = f"{self._model}-{device_id}-{kind.lower()}"
        except Exception as e:
            _LOGGER.error("Failed retrieving unique_id: %s", e)
            raise PlatformNotReady
        self._attrs: dict[str, Any] = {}
        self.kind = kind

    @property
    def state(self) -> StateType:
        value = self._device_status[self.kind]
        convert = self._description.get(ATTR_VALUE)
        if convert:
            value = convert(value, self._device_status)
        return cast(StateType, value)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.kind == PHILIPS_FILTER_PRE_REMAINING:
            self._attrs[ATTR_FILTER_PRE_REMAINING_RAW] = self._device_status[
                PHILIPS_FILTER_PRE_REMAINING
            ]
        if self.kind == PHILIPS_FILTER_HEPA_REMAINING:
            self._attrs[ATTR_FILTER_HEPA_TYPE] = self._device_status[PHILIPS_FILTER_HEPA_TYPE]
            self._attrs[ATTR_FILTER_HEPA_REMAINING_RAW] = self._device_status[
                PHILIPS_FILTER_HEPA_REMAINING
            ]
        if self.kind == PHILIPS_FILTER_ACTIVE_CARBON_REMAINING:
            self._attrs[ATTR_FILTER_ACTIVE_CARBON_TYPE] = self._device_status[
                PHILIPS_FILTER_ACTIVE_CARBON_TYPE
            ]
            self._attrs[ATTR_FILTER_ACTIVE_CARBON_REMAINING_RAW] = self._device_status[
                PHILIPS_FILTER_ACTIVE_CARBON_REMAINING
            ]
        if self.kind == PHILIPS_FILTER_WICK_REMAINING:
            self._attrs[ATTR_FILTER_WICK_REMAINING_RAW] = self._device_status[
                PHILIPS_FILTER_WICK_REMAINING
            ]
        return self._attrs
