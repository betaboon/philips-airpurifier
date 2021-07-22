"""Constants for Philips AirPurifier integration."""
from __future__ import annotations

from datetime import timedelta
from homeassistant.components.sensor import ATTR_STATE_CLASS, STATE_CLASS_MEASUREMENT
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_TEMPERATURE,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
)

from .model import SensorDescription

DOMAIN = "philips_airpurifier_coap"

DATA_KEY_CLIENT = "client"
DATA_KEY_COORDINATOR = "coordinator"
DATA_KEY_FAN = "fan"

DEFAULT_NAME = "Philips AirPurifier"
DEFAULT_ICON = "mdi:air-purifier"

CONF_MODEL = "model"

MODEL_AC1214 = "ac1214"
MODEL_AC2729 = "ac2729"
MODEL_AC2889 = "ac2889"
MODEL_AC2939 = "ac2939"
MODEL_AC2958 = "ac2958"
MODEL_AC3033 = "ac3033"
MODEL_AC3059 = "ac3059"
MODEL_AC3829 = "ac3829"
MODEL_AC3858 = "ac3858"
MODEL_AC4236 = "ac4236"

PRESET_MODE_SPEED_1 = "1"
PRESET_MODE_SPEED_2 = "2"
PRESET_MODE_SPEED_3 = "3"
PRESET_MODE_ALLERGEN = "allergen"
PRESET_MODE_AUTO = "auto"
PRESET_MODE_BACTERIA = "bacteria"
PRESET_MODE_GENTLE = "gentle"
PRESET_MODE_NIGHT = "night"
PRESET_MODE_SLEEP = "sleep"
PRESET_MODE_TURBO = "turbo"

FUNCTION_PURIFICATION = "purification"
FUNCTION_PURIFICATION_HUMIDIFICATION = "purification_humidification"

SERVICE_SET_CHILD_LOCK_OFF = "set_child_lock_off"
SERVICE_SET_CHILD_LOCK_ON = "set_child_lock_on"
SERVICE_SET_DISPLAY_BACKLIGHT_OFF = "set_display_backlight_off"
SERVICE_SET_DISPLAY_BACKLIGHT_ON = "set_display_backlight_on"
SERVICE_SET_FUNCTION = "set_function"
SERVICE_SET_HUMIDITY_TARGET = "set_humidity_target"
SERVICE_SET_LIGHT_BRIGHTNESS = "set_light_brightness"

ATTR_AIR_QUALITY_INDEX = "air_quality_index"
ATTR_CHILD_LOCK = "child_lock"
ATTR_DEVICE_ID = "device_id"
ATTR_DEVICE_VERSION = "device_version"
ATTR_DISPLAY_BACKLIGHT = "display_backlight"
ATTR_ERROR_CODE = "error_code"
ATTR_ERROR = "error"
ATTR_FILTER_ACTIVE_CARBON_REMAINING = "filter_active_carbon_remaining"
ATTR_FILTER_ACTIVE_CARBON_REMAINING_RAW = "filter_active_carbon_remaining_raw"
ATTR_FILTER_ACTIVE_CARBON_TYPE = "filter_active_carbon_type"
ATTR_FILTER_HEPA_REMAINING = "filter_hepa_remaining"
ATTR_FILTER_HEPA_REMAINING_RAW = "filter_hepa_remaining_raw"
ATTR_FILTER_HEPA_TYPE = "filter_hepa_type"
ATTR_FILTER_PRE_REMAINING = "filter_pre_remaining"
ATTR_FILTER_PRE_REMAINING_RAW = "filter_pre_remaining_raw"
ATTR_FILTER_WICK_REMAINING = "filter_wick_remaining"
ATTR_FILTER_WICK_REMAINING_RAW = "filter_wick_remaining_raw"
ATTR_FUNCTION = "function"
ATTR_HUMIDITY = "humidity"
ATTR_HUMIDITY_TARGET = "humidity_target"
ATTR_INDOOR_ALLERGEN_INDEX = "indoor_allergen_index"
ATTR_LABEL = "label"
ATTR_UNIT = "unit"
ATTR_VALUE = "value"
ATTR_LANGUAGE = "language"
ATTR_LIGHT_BRIGHTNESS = "light_brightness"
ATTR_MODE = "mode"
ATTR_MODEL_ID = "model_id"
ATTR_NAME = "name"
ATTR_PM25 = "pm25"
ATTR_PREFERRED_INDEX = "preferred_index"
ATTR_PRODUCT_ID = "product_id"
ATTR_RUNTIME = "runtime"
ATTR_SOFTWARE_VERSION = "software_version"
ATTR_SPEED = "speed"
ATTR_TOTAL_VOLATILE_ORGANIC_COMPOUNDS = "total_volatile_organic_compounds"
ATTR_TYPE = "type"
ATTR_WATER_LEVEL = "water_level"
ATTR_WIFI_VERSION = "wifi_version"

PHILIPS_AIR_QUALITY_INDEX = "aqit"
PHILIPS_CHILD_LOCK = "cl"
PHILIPS_DEVICE_ID = "DeviceId"
PHILIPS_DEVICE_VERSION = "DeviceVersion"
PHILIPS_DISPLAY_BACKLIGHT = "uil"
PHILIPS_ERROR_CODE = "err"
PHILIPS_FILTER_ACTIVE_CARBON_REMAINING = "fltsts2"
PHILIPS_FILTER_ACTIVE_CARBON_TYPE = "fltt2"
PHILIPS_FILTER_HEPA_REMAINING = "fltsts1"
PHILIPS_FILTER_HEPA_TYPE = "fltt1"
PHILIPS_FILTER_PRE_REMAINING = "fltsts0"
PHILIPS_FILTER_WICK_REMAINING = "wicksts"
PHILIPS_FUNCTION = "func"
PHILIPS_HUMIDITY = "rh"
PHILIPS_HUMIDITY_TARGET = "rhset"
PHILIPS_INDOOR_ALLERGEN_INDEX = "iaql"
PHILIPS_LANGUAGE = "language"
PHILIPS_LIGHT_BRIGHTNESS = "aqil"
PHILIPS_MODE = "mode"
PHILIPS_MODEL_ID = "modelid"
PHILIPS_NAME = "name"
PHILIPS_PM25 = "pm25"
PHILIPS_POWER = "pwr"
PHILIPS_PREFERRED_INDEX = "ddp"
PHILIPS_PRODUCT_ID = "ProductId"
PHILIPS_RUNTIME = "Runtime"
PHILIPS_SOFTWARE_VERSION = "swversion"
PHILIPS_SPEED = "om"
PHILIPS_TEMPERATURE = "temp"
PHILIPS_TOTAL_VOLATILE_ORGANIC_COMPOUNDS = "tvoc"
PHILIPS_TYPE = "type"
PHILIPS_WATER_LEVEL = "wl"
PHILIPS_WIFI_VERSION = "WifiVersion"

PHILIPS_PREFERRED_INDEX_MAP = {
    "0": "Indoor Allergen Index",
    "1": "PM2.5",
    "2": "Gas",
}
PHILIPS_DISPLAY_BACKLIGHT_MAP = {
    "0": False,
    "1": True,
}
PHILIPS_FUNCTION_MAP = {
    "P": "Purification",
    "PH": "Purification and Humidification",
}
PHILIPS_ERROR_CODE_MAP = {
    32768: "no water",
    49153: "pre-filter must be cleaned",
    49155: "pre-filter must be cleaned",
    49408: "no water",
}

SENSOR_TYPES: dict[str, SensorDescription] = {
    # filter information
    PHILIPS_FILTER_PRE_REMAINING: {
        ATTR_LABEL: ATTR_FILTER_PRE_REMAINING,
        ATTR_VALUE: lambda value, _: str(timedelta(hours=value)),
    },
    PHILIPS_FILTER_HEPA_REMAINING: {
        ATTR_LABEL: ATTR_FILTER_HEPA_REMAINING,
        ATTR_VALUE: lambda value, _: str(timedelta(hours=value)),
    },
    PHILIPS_FILTER_ACTIVE_CARBON_REMAINING: {
        ATTR_LABEL: ATTR_FILTER_ACTIVE_CARBON_REMAINING,
        ATTR_VALUE: lambda value, _: str(timedelta(hours=value)),
    },
    PHILIPS_FILTER_WICK_REMAINING: {
        ATTR_LABEL: ATTR_FILTER_WICK_REMAINING,
        ATTR_VALUE: lambda value, _: str(timedelta(hours=value)),
    },
    PHILIPS_WATER_LEVEL: {
        ATTR_ICON: "mdi:water",
        ATTR_LABEL: ATTR_WATER_LEVEL,
        ATTR_VALUE: lambda value, status: 0 if status.get("err") in [32768, 49408] else value,
    },
    # device sensors
    PHILIPS_AIR_QUALITY_INDEX: {
        ATTR_LABEL: ATTR_AIR_QUALITY_INDEX,
    },
    PHILIPS_INDOOR_ALLERGEN_INDEX: {
        ATTR_ICON: "mdi:blur",
        ATTR_LABEL: ATTR_INDOOR_ALLERGEN_INDEX,
        ATTR_STATE_CLASS: STATE_CLASS_MEASUREMENT,
    },
    PHILIPS_PM25: {
        ATTR_ICON: "mdi:blur",
        ATTR_LABEL: "PM2.5",
        ATTR_UNIT: CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        ATTR_STATE_CLASS: STATE_CLASS_MEASUREMENT,
    },
    PHILIPS_TOTAL_VOLATILE_ORGANIC_COMPOUNDS: {
        ATTR_ICON: "mdi:blur",
        ATTR_LABEL: ATTR_TOTAL_VOLATILE_ORGANIC_COMPOUNDS,
        ATTR_STATE_CLASS: STATE_CLASS_MEASUREMENT,
    },
    PHILIPS_HUMIDITY: {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_HUMIDITY,
        ATTR_LABEL: ATTR_HUMIDITY,
        ATTR_STATE_CLASS: STATE_CLASS_MEASUREMENT,
    },
    PHILIPS_TEMPERATURE: {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_LABEL: ATTR_TEMPERATURE,
        ATTR_STATE_CLASS: STATE_CLASS_MEASUREMENT,
    },
}
