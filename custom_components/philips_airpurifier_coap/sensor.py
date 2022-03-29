"""Philips Air Purifier & Humidifier Sensors"""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Callable, List, cast

from homeassistant.components.sensor import ATTR_STATE_CLASS, SensorEntity
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    CONF_HOST,
    CONF_NAME,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, StateType

from . import Coordinator, PhilipsEntity
from .const import (
    ATTR_LABEL,
    ATTR_POSTFIX,
    ATTR_PREFIX,
    ATTR_RAW,
    ATTR_TIME_REMAINING,
    ATTR_TOTAL,
    ATTR_TYPE,
    ATTR_UNIT,
    ATTR_VALUE,
    CONF_MODEL,
    DATA_KEY_COORDINATOR,
    DOMAIN,
    FILTER_TYPES,
    PHILIPS_DEVICE_ID,
    PHILIPS_FILTER_STATUS,
    PHILIPS_FILTER_TOTAL,
    PHILIPS_FILTER_TYPE,
    SENSOR_TYPES,
)
from .model import DeviceStatus

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
    for filter in FILTER_TYPES:
        if PhilipsFilterSensor.is_supported(coordinator.status, filter):
            sensors.append(PhilipsFilterSensor(coordinator, name, model, filter))

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


class PhilipsFilterSensor(PhilipsEntity, SensorEntity):
    """Define a Philips AirPurifier filter sensor."""

    @classmethod
    def is_supported(cls, device_status: DeviceStatus, kind: str) -> bool:
        description = FILTER_TYPES[kind]
        prefix = description[ATTR_PREFIX]
        postfix = description[ATTR_POSTFIX]
        return "".join([prefix, PHILIPS_FILTER_STATUS, postfix]) in device_status

    def __init__(self, coordinator: Coordinator, name: str, model: str, kind: str) -> None:
        super().__init__(coordinator)
        self._model = model
        description = FILTER_TYPES[kind]
        prefix = description[ATTR_PREFIX]
        postfix = description[ATTR_POSTFIX]
        self._value_key = "".join([prefix, PHILIPS_FILTER_STATUS, postfix])
        self._total_key = "".join([prefix, PHILIPS_FILTER_TOTAL, postfix])
        self._type_key = "".join([prefix, PHILIPS_FILTER_TYPE, postfix])

        if self._has_total:
            self._attr_unit_of_measurement = PERCENTAGE
        self._attr_name = f"{name} {kind.replace('_', ' ').title()}"
        try:
            device_id = self._device_status[PHILIPS_DEVICE_ID]
            self._attr_unique_id = f"{self._model}-{device_id}-{kind}"
        except Exception as e:
            _LOGGER.error("Failed retrieving unique_id: %s", e)
            raise PlatformNotReady
        self._attrs: dict[str, Any] = {}

    @property
    def state(self) -> StateType:
        if self._has_total:
            return self._percentage
        else:
            return self._time_remaining

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self._type_key in self._device_status:
            self._attrs[ATTR_TYPE] = self._device_status[self._type_key]
        self._attrs[ATTR_RAW] = self._value
        if self._has_total:
            self._attrs[ATTR_TOTAL] = self._total
            self._attrs[ATTR_TIME_REMAINING] = self._time_remaining
        return self._attrs

    @property
    def _has_total(self) -> bool:
        return self._total_key in self._device_status

    @property
    def _percentage(self) -> float:
        return round(100.0 * self._value / self._total, 2)

    @property
    def _time_remaining(self) -> str:
        return str(timedelta(hours=self._value))

    @property
    def _value(self) -> int:
        return self._device_status[self._value_key]

    @property
    def _total(self) -> int:
        return self._device_status[self._total_key]
