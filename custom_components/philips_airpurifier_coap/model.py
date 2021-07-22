"""Type definitions for Philips AirPurifier integration."""
from __future__ import annotations

from typing import Any, Callable, TypedDict

from homeassistant.helpers.typing import StateType


DeviceStatus = dict[str, Any]


class _SensorDescription(TypedDict):
    """Mandatory attributes for a sensor description."""

    label: str


class SensorDescription(_SensorDescription, total=False):
    """Sensor description class."""

    device_class: str
    icon: str
    unit: str
    state_class: str
    value: Callable[[Any, DeviceStatus], StateType]
