"""Philips Air Purifier & Humidifier"""
import asyncio
import logging
from datetime import timedelta
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Union,
)

from homeassistant.components.fan import (
    FanEntity,
    PLATFORM_SCHEMA,
    SUPPORT_PRESET_MODE,
)
from homeassistant.components.light import ATTR_BRIGHTNESS
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
    CONF_HOST,
    CONF_ICON,
    CONF_NAME,
)
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import voluptuous as vol
from aioairctrl import CoAPClient

from .const import (
    ATTR_AIR_QUALITY_INDEX,
    ATTR_CHILD_LOCK,
    ATTR_DEVICE_ID,
    ATTR_DEVICE_VERSION,
    ATTR_DISPLAY_BACKLIGHT,
    ATTR_ERROR,
    ATTR_ERROR_CODE,
    ATTR_FILTER_ACTIVE_CARBON_REMAINING,
    ATTR_FILTER_ACTIVE_CARBON_REMAINING_RAW,
    ATTR_FILTER_ACTIVE_CARBON_TYPE,
    ATTR_FILTER_HEPA_REMAINING,
    ATTR_FILTER_HEPA_REMAINING_RAW,
    ATTR_FILTER_HEPA_TYPE,
    ATTR_FILTER_PRE_REMAINING,
    ATTR_FILTER_PRE_REMAINING_RAW,
    ATTR_FILTER_WICK_REMAINING,
    ATTR_FILTER_WICK_REMAINING_RAW,
    ATTR_FUNCTION,
    ATTR_HUMIDITY,
    ATTR_HUMIDITY_TARGET,
    ATTR_INDOOR_ALLERGEN_INDEX,
    ATTR_LANGUAGE,
    ATTR_LIGHT_BRIGHTNESS,
    ATTR_MODEL_ID,
    ATTR_NAME,
    ATTR_PM25,
    ATTR_PREFERRED_INDEX,
    ATTR_PRODUCT_ID,
    ATTR_RUNTIME,
    ATTR_SOFTWARE_VERSION,
    ATTR_TOTAL_VOLATILE_ORGANIC_COMPOUNDS,
    ATTR_TYPE,
    ATTR_WATER_LEVEL,
    ATTR_WIFI_VERSION,
    CONF_MODEL,
    DATA_KEY,
    DEFAULT_ICON,
    DEFAULT_NAME,
    DOMAIN,
    FUNCTION_PURIFICATION,
    FUNCTION_PURIFICATION_HUMIDIFICATION,
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
    PHILIPS_AIR_QUALITY_INDEX,
    PHILIPS_CHILD_LOCK,
    PHILIPS_DEVICE_ID,
    PHILIPS_DEVICE_VERSION,
    PHILIPS_DISPLAY_BACKLIGHT,
    PHILIPS_DISPLAY_BACKLIGHT_MAP,
    PHILIPS_ERROR_CODE,
    PHILIPS_ERROR_CODE_MAP,
    PHILIPS_FILTER_ACTIVE_CARBON_REMAINING,
    PHILIPS_FILTER_ACTIVE_CARBON_TYPE,
    PHILIPS_FILTER_HEPA_REMAINING,
    PHILIPS_FILTER_HEPA_TYPE,
    PHILIPS_FILTER_PRE_REMAINING,
    PHILIPS_FILTER_WICK_REMAINING,
    PHILIPS_FUNCTION,
    PHILIPS_FUNCTION_MAP,
    PHILIPS_HUMIDITY,
    PHILIPS_HUMIDITY_TARGET,
    PHILIPS_INDOOR_ALLERGEN_INDEX,
    PHILIPS_LANGUAGE,
    PHILIPS_LIGHT_BRIGHTNESS,
    PHILIPS_MODE,
    PHILIPS_MODEL_ID,
    PHILIPS_NAME,
    PHILIPS_PM25,
    PHILIPS_POWER,
    PHILIPS_PREFERRED_INDEX,
    PHILIPS_PREFERRED_INDEX_MAP,
    PHILIPS_PRODUCT_ID,
    PHILIPS_RUNTIME,
    PHILIPS_SOFTWARE_VERSION,
    PHILIPS_SPEED,
    PHILIPS_TEMPERATURE,
    PHILIPS_TOTAL_VOLATILE_ORGANIC_COMPOUNDS,
    PHILIPS_TYPE,
    PHILIPS_WATER_LEVEL,
    PHILIPS_WIFI_VERSION,
    SERVICE_SET_CHILD_LOCK_OFF,
    SERVICE_SET_CHILD_LOCK_ON,
    SERVICE_SET_DISPLAY_BACKLIGHT_OFF,
    SERVICE_SET_DISPLAY_BACKLIGHT_ON,
    SERVICE_SET_FUNCTION,
    SERVICE_SET_HUMIDITY_TARGET,
    SERVICE_SET_LIGHT_BRIGHTNESS,
    PRESET_MODE_SPEED_1,
    PRESET_MODE_SPEED_2,
    PRESET_MODE_SPEED_3,
    PRESET_MODE_ALLERGEN,
    PRESET_MODE_AUTO,
    PRESET_MODE_BACTERIA,
    PRESET_MODE_GENTLE,
    PRESET_MODE_NIGHT,
    PRESET_MODE_SLEEP,
    PRESET_MODE_TURBO,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
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
    }
)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable[[List[Entity], bool], None],
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    host = config[CONF_HOST]
    model = config[CONF_MODEL]
    name = config[CONF_NAME]
    icon = config[CONF_ICON]

    model_to_class = {
        MODEL_AC1214: PhilipsAC1214,
        MODEL_AC2729: PhilipsAC2729,
        MODEL_AC2889: PhilipsAC2889,
        MODEL_AC2939: PhilipsAC2939,
        MODEL_AC2958: PhilipsAC2958,
        MODEL_AC3033: PhilipsAC3033,
        MODEL_AC3059: PhilipsAC3059,
        MODEL_AC3829: PhilipsAC3829,
        MODEL_AC3858: PhilipsAC3858,
        MODEL_AC4236: PhilipsAC4236,
    }

    model_class = model_to_class.get(model)
    if model_class:
        device = model_class(host=host, model=model, name=name, icon=icon)
        await device.init()
    else:
        _LOGGER.error("Unsupported model: %s", model)
        return False

    if DATA_KEY not in hass.data:
        hass.data[DATA_KEY] = []
    hass.data[DATA_KEY].append(device)
    async_add_entities([device], update_before_add=True)

    def wrapped_async_register(
        domain: str,
        service: str,
        service_func: Callable,
        schema: Optional[vol.Schema] = None,
    ):
        async def service_func_wrapper(service_call):
            service_data = service_call.data.copy()
            entity_id = service_data.pop("entity_id", None)
            devices = [d for d in hass.data[DATA_KEY] if d.entity_id == entity_id]
            for d in devices:
                device_service_func = getattr(d, service_func.__name__)
                return await device_service_func(**service_data)

        hass.services.async_register(
            domain=domain,
            service=service,
            service_func=service_func_wrapper,
            schema=schema,
        )

    device._register_services(wrapped_async_register)


class PhilipsGenericFan(FanEntity):
    def __init__(self, host: str, model: str, name: str, icon: str) -> None:
        self._host = host
        self._model = model
        self._name = name
        self._icon = icon
        self._available = False
        self._state = None
        self._unique_id = None

    async def init(self) -> None:
        pass

    async def async_added_to_hass(self) -> None:
        pass

    async def async_will_remove_from_hass(self) -> None:
        pass

    def _register_services(self, async_register) -> None:
        for cls in reversed(self.__class__.__mro__):
            register_method = getattr(cls, "register_services", None)
            if callable(register_method):
                register_method(self, async_register)

    def register_services(self, async_register) -> None:
        pass

    @property
    def unique_id(self) -> Optional[str]:
        return self._unique_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str:
        return self._icon

    @property
    def available(self) -> bool:
        return self._available


class Timer:
    _in_callback: bool = False
    _auto_restart:bool = False

    def __init__(self, timeout, callback, autostart=True):
        self._timeout = timeout
        self._callback = callback
        self._task = None

        if autostart:
            self.start()

    async def _job(self):
        while True:
            try:
                self._in_callback = False
                _LOGGER.debug(f"Starte Timer {self._timeout}s.")
                await asyncio.sleep(self._timeout)
                self._in_callback = True
                _LOGGER.info("Calling timeout callback...")
                await self._callback()
                _LOGGER.debug("Timeout callback finished!")
            except asyncio.exceptions.CancelledError:
                _LOGGER.debug("Timer cancelled")
            except:
                _LOGGER.exception("Timer callback failure")
            self._in_callback = False
            if not self._auto_restart:
                break

    def setTimeout(self, timeout):
        self._timeout = timeout

    def _cancel(self):
        if self._in_callback:
            raise Exception("Timedout too late to cancel!")
        if self._task is not None:
            self._task.cancel()
    
    def reset(self):
        self._cancel()
        self.start()

    def start(self):
        self._task = asyncio.ensure_future(self._job())

class PhilipsGenericCoAPFanBase(PhilipsGenericFan):
    AVAILABLE_PRESET_MODES = {}
    AVAILABLE_ATTRIBUTES = []

    def __init__(self, host: str, model: str, name: str, icon: str) -> None:
        super().__init__(host, model, name, icon)
        self._device_status = None
        self._timer: Timer = Timer(70, self.reset_connection, False) # Maybe use response.opts.max_age field here, instead of hardcoding?
        self._connecting_timeout = Timer(20, self.stopConnectingAttempt, False)

        self._connect_task = None
        self._reconnect_time = 1

        self._preset_modes = []
        self._available_preset_modes = {}
        self._collect_available_preset_modes()

        self._available_attributes = []
        self._collect_available_attributes()

    async def stopConnectingAttempt(self):
        _LOGGER.debug("Try to cancel connect...")
        if self._connect_task is not None:
            _LOGGER.debug("Try to cancel connect......")
            self._connect_task.cancel()

    async def reset_connection(self, endIt=False):
        try:
            if self._observer_task is not None:
                self._observer_task.cancel()
                try:
                    await self._observer_task
                except asyncio.exceptions.CancelledError:
                    pass # Silently ignore, because we cancelled 4 lines above
            if self._client is not None:
                await self._client.shutdown()
        except:
            _LOGGER.exception("Reset Connection: Cleanup of old connection failed!")
        if not endIt:
            await self.init()
            await self.async_added_to_hass()

    async def init_connection(self):
        self._client = await CoAPClient.create(self._host)
        self._observer_task = None
        try:
            status = await self._client.get_status()
            device_id = status[PHILIPS_DEVICE_ID]
            self._unique_id = f"{self._model}-{device_id}"
            self._device_status = status
        except Exception as e:
            _LOGGER.error("Failed retrieving unique_id: %s", e)
            raise PlatformNotReady

    async def init(self) -> None:
        while True:
            try:
                _LOGGER.info("Connecting to AirPurifier...")
                self._connecting_timeout.reset()
                self._connect_task = asyncio.ensure_future(self.init_connection())
                await self._connect_task
                self._connect_task.result()
                self._connect_task = None
                self._connecting_timeout._cancel()
                _LOGGER.debug("Starte Oberservation Timeout...")
                self._timer.start()
                return
            except asyncio.exceptions.CancelledError:
                pass # We got cancelled, return immediately
            except:
                if self._device_status is not None:
                    self._device_status = None
                    self.schedule_update_ha_state()
                _LOGGER.exception("init_connection(): Exception!")
                await asyncio.sleep(self._reconnect_time)
                self._reconnect_time = 60 if self._reconnect_time > 60 else self._reconnect_time * 1.5
        

    def _collect_available_preset_modes(self):
        preset_modes = {}
        for cls in reversed(self.__class__.__mro__):
            cls_preset_modes = getattr(cls, "AVAILABLE_PRESET_MODES", {})
            preset_modes.update(cls_preset_modes)
        self._available_preset_modes = preset_modes
        self._preset_modes = list(self._available_preset_modes.keys())

    def _collect_available_attributes(self):
        attributes = []
        for cls in reversed(self.__class__.__mro__):
            cls_attributes = getattr(cls, "AVAILABLE_ATTRIBUTES", [])
            attributes.extend(cls_attributes)
        self._available_attributes = attributes

    async def async_added_to_hass(self) -> None:
        self._observer_task = asyncio.create_task(self._observe_status())

    async def async_will_remove_from_hass(self) -> None:
        await self.reset_connection(endIt=True)

    async def _observe_status(self) -> None:
        async for status in self._client.observe_status():
            self._device_status = status
            self.schedule_update_ha_state()
            self._timer.reset()

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def available(self):
        return self._device_status is not None

    @property
    def is_on(self) -> bool:
        return self._device_status.get(PHILIPS_POWER) == "1"

    async def async_turn_on(
        self,
        speed: Optional[str] = None,
        percentage: Optional[int] = None,
        preset_mode: Optional[str] = None,
        **kwargs,
    ):
        if preset_mode:
            await self.async_set_preset_mode(preset_mode)
        else:
            await self._client.set_control_value(PHILIPS_POWER, "1")

    async def async_turn_off(self, **kwargs) -> None:
        await self._client.set_control_value(PHILIPS_POWER, "0")

    @property
    def supported_features(self) -> int:
        return SUPPORT_PRESET_MODE

    @property
    def preset_modes(self) -> Optional[List[str]]:
        return self._preset_modes

    @property
    def preset_mode(self) -> Optional[str]:
        for preset_mode, status_pattern in self._available_preset_modes.items():
            for k, v in status_pattern.items():
                if self._device_status.get(k) != v:
                    break
            else:
                return preset_mode

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        status_pattern = self._available_preset_modes.get(preset_mode)
        if status_pattern:
            await self._client.set_control_values(data=status_pattern)

    @property
    def device_state_attributes(self) -> Optional[Dict[str, Any]]:
        def append(
            attributes: dict,
            key: str,
            philips_key: str,
            value_map: Union[dict, Callable[[Any, Any], Any]] = None,
        ):
            if philips_key in self._device_status:
                value = self._device_status[philips_key]
                if isinstance(value_map, dict) and value in value_map:
                    value = value_map.get(value, "unknown")
                elif callable(value_map):
                    value = value_map(value, self._device_status)
                attributes.update({key: value})

        device_attributes = dict()
        for key, philips_key, *rest in self._available_attributes:
            value_map = rest[0] if len(rest) else None
            append(device_attributes, key, philips_key, value_map)
        return device_attributes


class PhilipsGenericCoAPFan(PhilipsGenericCoAPFanBase):
    AVAILABLE_PRESET_MODES = {}

    AVAILABLE_ATTRIBUTES = [
        # device information
        (ATTR_NAME, PHILIPS_NAME),
        (ATTR_TYPE, PHILIPS_TYPE),
        (ATTR_MODEL_ID, PHILIPS_MODEL_ID),
        (ATTR_PRODUCT_ID, PHILIPS_PRODUCT_ID),
        (ATTR_DEVICE_ID, PHILIPS_DEVICE_ID),
        (ATTR_DEVICE_VERSION, PHILIPS_DEVICE_VERSION),
        (ATTR_SOFTWARE_VERSION, PHILIPS_SOFTWARE_VERSION),
        (ATTR_WIFI_VERSION, PHILIPS_WIFI_VERSION),
        (ATTR_ERROR_CODE, PHILIPS_ERROR_CODE),
        (ATTR_ERROR, PHILIPS_ERROR_CODE, PHILIPS_ERROR_CODE_MAP),
        # device configuration
        (ATTR_LANGUAGE, PHILIPS_LANGUAGE),
        (ATTR_CHILD_LOCK, PHILIPS_CHILD_LOCK),
        (ATTR_LIGHT_BRIGHTNESS, PHILIPS_LIGHT_BRIGHTNESS),
        (ATTR_DISPLAY_BACKLIGHT, PHILIPS_DISPLAY_BACKLIGHT, PHILIPS_DISPLAY_BACKLIGHT_MAP),
        (ATTR_PREFERRED_INDEX, PHILIPS_PREFERRED_INDEX, PHILIPS_PREFERRED_INDEX_MAP),
        # filter information
        (
            ATTR_FILTER_PRE_REMAINING,
            PHILIPS_FILTER_PRE_REMAINING,
            lambda x, _: str(timedelta(hours=x)),
        ),
        (ATTR_FILTER_PRE_REMAINING_RAW, PHILIPS_FILTER_PRE_REMAINING),
        (ATTR_FILTER_HEPA_TYPE, PHILIPS_FILTER_HEPA_TYPE),
        (
            ATTR_FILTER_HEPA_REMAINING,
            PHILIPS_FILTER_HEPA_REMAINING,
            lambda x, _: str(timedelta(hours=x)),
        ),
        (ATTR_FILTER_HEPA_REMAINING_RAW, PHILIPS_FILTER_HEPA_REMAINING),
        (ATTR_FILTER_ACTIVE_CARBON_TYPE, PHILIPS_FILTER_ACTIVE_CARBON_TYPE),
        (
            ATTR_FILTER_ACTIVE_CARBON_REMAINING,
            PHILIPS_FILTER_ACTIVE_CARBON_REMAINING,
            lambda x, _: str(timedelta(hours=x)),
        ),
        (ATTR_FILTER_ACTIVE_CARBON_REMAINING_RAW, PHILIPS_FILTER_ACTIVE_CARBON_REMAINING),
        # device sensors
        (ATTR_RUNTIME, PHILIPS_RUNTIME, lambda x, _: str(timedelta(seconds=round(x / 1000)))),
        (ATTR_AIR_QUALITY_INDEX, PHILIPS_AIR_QUALITY_INDEX),
        (ATTR_INDOOR_ALLERGEN_INDEX, PHILIPS_INDOOR_ALLERGEN_INDEX),
        (ATTR_PM25, PHILIPS_PM25),
    ]

    SERVICE_SCHEMA_SET_LIGHT_BRIGHTNESS = vol.Schema(
        {
            vol.Required(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required(ATTR_BRIGHTNESS): vol.All(vol.Coerce(int), vol.Clamp(min=0, max=100)),
        }
    )

    def register_services(self, async_register):
        async_register(
            domain=DOMAIN,
            service=SERVICE_SET_CHILD_LOCK_ON,
            service_func=self.async_set_child_lock_on,
        )
        async_register(
            domain=DOMAIN,
            service=SERVICE_SET_CHILD_LOCK_OFF,
            service_func=self.async_set_child_lock_off,
        )
        async_register(
            domain=DOMAIN,
            service=SERVICE_SET_DISPLAY_BACKLIGHT_ON,
            service_func=self.async_set_display_backlight_on,
        )
        async_register(
            domain=DOMAIN,
            service=SERVICE_SET_DISPLAY_BACKLIGHT_OFF,
            service_func=self.async_set_display_backlight_off,
        )
        async_register(
            domain=DOMAIN,
            service=SERVICE_SET_LIGHT_BRIGHTNESS,
            service_func=self.async_set_light_brightness,
            schema=self.SERVICE_SCHEMA_SET_LIGHT_BRIGHTNESS,
        )

    async def async_set_child_lock_on(self):
        await self._client.set_control_value(PHILIPS_CHILD_LOCK, True)

    async def async_set_child_lock_off(self):
        await self._client.set_control_value(PHILIPS_CHILD_LOCK, False)

    async def async_set_display_backlight_on(self):
        await self._client.set_control_value(PHILIPS_DISPLAY_BACKLIGHT, "1")

    async def async_set_display_backlight_off(self):
        await self._client.set_control_value(PHILIPS_DISPLAY_BACKLIGHT, "0")

    async def async_set_light_brightness(self, brightness: int):
        await self._client.set_control_value(PHILIPS_LIGHT_BRIGHTNESS, brightness)


class PhilipsTVOCMixin(PhilipsGenericCoAPFanBase):
    AVAILABLE_ATTRIBUTES = [
        (ATTR_TOTAL_VOLATILE_ORGANIC_COMPOUNDS, PHILIPS_TOTAL_VOLATILE_ORGANIC_COMPOUNDS),
    ]


class PhilipsFilterWickMixin(PhilipsGenericCoAPFanBase):
    AVAILABLE_ATTRIBUTES = [
        (
            ATTR_FILTER_WICK_REMAINING,
            PHILIPS_FILTER_WICK_REMAINING,
            lambda x, _: str(timedelta(hours=x)),
        ),
        (ATTR_FILTER_WICK_REMAINING_RAW, PHILIPS_FILTER_WICK_REMAINING),
    ]


class PhilipsHumidifierMixin(PhilipsGenericCoAPFanBase):
    AVAILABLE_ATTRIBUTES = [
        (ATTR_FUNCTION, PHILIPS_FUNCTION, PHILIPS_FUNCTION_MAP),
        (ATTR_HUMIDITY, PHILIPS_HUMIDITY),
        (ATTR_HUMIDITY_TARGET, PHILIPS_HUMIDITY_TARGET),
        (ATTR_TEMPERATURE, PHILIPS_TEMPERATURE),
    ]

    SERVICE_SCHEMA_SET_FUNCTION = vol.Schema(
        {
            vol.Required(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required(ATTR_FUNCTION): vol.In(
                [
                    FUNCTION_PURIFICATION,
                    FUNCTION_PURIFICATION_HUMIDIFICATION,
                ]
            ),
        }
    )

    SERVICE_SCHEMA_SET_HUMIDITY_TARGET = vol.Schema(
        {
            vol.Required(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required(ATTR_HUMIDITY_TARGET): vol.All(
                vol.Coerce(int),
                vol.In([40, 50, 60, 70]),
            ),
        }
    )

    def register_services(self, async_register) -> None:
        async_register(
            domain=DOMAIN,
            service=SERVICE_SET_FUNCTION,
            service_func=self.async_set_function,
            schema=self.SERVICE_SCHEMA_SET_FUNCTION,
        )
        async_register(
            domain=DOMAIN,
            service=SERVICE_SET_HUMIDITY_TARGET,
            service_func=self.async_set_humidity_target,
            schema=self.SERVICE_SCHEMA_SET_HUMIDITY_TARGET,
        )

    async def async_set_function(self, function: str) -> None:
        if function == FUNCTION_PURIFICATION:
            await self._client.set_control_value(PHILIPS_FUNCTION, "P")
        elif function == FUNCTION_PURIFICATION_HUMIDIFICATION:
            await self._client.set_control_value(PHILIPS_FUNCTION, "PH")

    async def async_set_humidity_target(self, humidity_target: int) -> None:
        await self._client.set_control_value(PHILIPS_HUMIDITY_TARGET, humidity_target)


class PhilipsWaterLevelMixin(PhilipsGenericCoAPFanBase):
    AVAILABLE_ATTRIBUTES = [
        (
            ATTR_WATER_LEVEL,
            PHILIPS_WATER_LEVEL,
            lambda x, y: 0 if y.get("err") in [32768, 49408] else x,
        ),
    ]


# TODO consolidate these classes as soon as we see a proper pattern
class PhilipsAC1214(PhilipsGenericCoAPFan):
    AVAILABLE_PRESET_MODES = {
        PRESET_MODE_SPEED_1: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "1"},
        PRESET_MODE_SPEED_2: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "2"},
        PRESET_MODE_SPEED_3: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "3"},
        PRESET_MODE_ALLERGEN: {PHILIPS_POWER: "1", PHILIPS_MODE: "A"},
        PRESET_MODE_AUTO: {PHILIPS_POWER: "1", PHILIPS_MODE: "P"},
        PRESET_MODE_NIGHT: {PHILIPS_POWER: "1", PHILIPS_MODE: "N"},
        PRESET_MODE_TURBO: {PHILIPS_POWER: "1", PHILIPS_MODE: "T", PHILIPS_SPEED: "t"},
    }


class PhilipsAC2729(
    PhilipsWaterLevelMixin,
    PhilipsHumidifierMixin,
    PhilipsFilterWickMixin,
    PhilipsGenericCoAPFan,
):
    AVAILABLE_PRESET_MODES = {
        PRESET_MODE_SPEED_1: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "1"},
        PRESET_MODE_SPEED_2: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "2"},
        PRESET_MODE_SPEED_3: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "3"},
        PRESET_MODE_ALLERGEN: {PHILIPS_POWER: "1", PHILIPS_MODE: "A"},
        PRESET_MODE_AUTO: {PHILIPS_POWER: "1", PHILIPS_MODE: "P"},
        PRESET_MODE_NIGHT: {PHILIPS_POWER: "1", PHILIPS_MODE: "S", PHILIPS_SPEED: "s"},
        PRESET_MODE_TURBO: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "t"},
    }


class PhilipsAC2889(PhilipsGenericCoAPFan):
    AVAILABLE_PRESET_MODES = {
        PRESET_MODE_SPEED_1: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "1"},
        PRESET_MODE_SPEED_2: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "2"},
        PRESET_MODE_SPEED_3: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "3"},
        PRESET_MODE_ALLERGEN: {PHILIPS_POWER: "1", PHILIPS_MODE: "A"},
        PRESET_MODE_AUTO: {PHILIPS_POWER: "1", PHILIPS_MODE: "P"},
        PRESET_MODE_BACTERIA: {PHILIPS_POWER: "1", PHILIPS_MODE: "B"},
        PRESET_MODE_SLEEP: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "s"},
        PRESET_MODE_TURBO: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "t"},
    }

class PhilipsAC2939(PhilipsTVOCMixin, PhilipsGenericCoAPFan):
    AVAILABLE_PRESET_MODES = {
        PRESET_MODE_AUTO: {PHILIPS_POWER: "1", PHILIPS_MODE: "AG"},
        PRESET_MODE_GENTLE: {PHILIPS_POWER: "1", PHILIPS_MODE: "GT"},
        PRESET_MODE_SLEEP: {PHILIPS_POWER: "1", PHILIPS_MODE: "S"},
        PRESET_MODE_TURBO: {PHILIPS_POWER: "1", PHILIPS_MODE: "T"},
    }

class PhilipsAC2958(PhilipsGenericCoAPFan):
    AVAILABLE_PRESET_MODES = {
        PRESET_MODE_AUTO: {PHILIPS_POWER: "1", PHILIPS_MODE: "AG"},
        PRESET_MODE_GENTLE: {PHILIPS_POWER: "1", PHILIPS_MODE: "GT"},
        PRESET_MODE_SLEEP: {PHILIPS_POWER: "1", PHILIPS_MODE: "S"},
        PRESET_MODE_TURBO: {PHILIPS_POWER: "1", PHILIPS_MODE: "T"},
    }

class PhilipsAC3033(PhilipsTVOCMixin, PhilipsGenericCoAPFan):
    AVAILABLE_PRESET_MODES = {
        PRESET_MODE_SPEED_1: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "1"},
        PRESET_MODE_SPEED_2: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "2"},
        PRESET_MODE_AUTO: {PHILIPS_POWER: "1", PHILIPS_MODE: "AG"},
        PRESET_MODE_SLEEP: {PHILIPS_POWER: "1", PHILIPS_MODE: "S", PHILIPS_SPEED: "s"},
        PRESET_MODE_TURBO: {PHILIPS_POWER: "1", PHILIPS_MODE: "T", PHILIPS_SPEED: "t"},
    }

class PhilipsAC3059(PhilipsTVOCMixin, PhilipsGenericCoAPFan):
    AVAILABLE_PRESET_MODES = {
        PRESET_MODE_SPEED_1: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "1"},
        PRESET_MODE_SPEED_2: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "2"},
        PRESET_MODE_AUTO: {PHILIPS_POWER: "1", PHILIPS_MODE: "AG"},
        PRESET_MODE_SLEEP: {PHILIPS_POWER: "1", PHILIPS_MODE: "S", PHILIPS_SPEED: "s"},
        PRESET_MODE_TURBO: {PHILIPS_POWER: "1", PHILIPS_MODE: "T", PHILIPS_SPEED: "t"},
    }


class PhilipsAC3829(PhilipsHumidifierMixin, PhilipsFilterWickMixin, PhilipsGenericCoAPFan):
    AVAILABLE_PRESET_MODES = {
        PRESET_MODE_SPEED_1: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "1"},
        PRESET_MODE_SPEED_2: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "2"},
        PRESET_MODE_SPEED_3: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "3"},
        PRESET_MODE_ALLERGEN: {PHILIPS_POWER: "1", PHILIPS_MODE: "A"},
        PRESET_MODE_AUTO: {PHILIPS_POWER: "1", PHILIPS_MODE: "P"},
        PRESET_MODE_SLEEP: {PHILIPS_POWER: "1", PHILIPS_MODE: "S", PHILIPS_SPEED: "s"},
        PRESET_MODE_TURBO: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "t"},
    }


class PhilipsAC3858(PhilipsTVOCMixin, PhilipsGenericCoAPFan):
    AVAILABLE_PRESET_MODES = {
        PRESET_MODE_SPEED_1: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "1"},
        PRESET_MODE_SPEED_2: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "2"},
        PRESET_MODE_AUTO: {PHILIPS_POWER: "1", PHILIPS_MODE: "AG"},
        PRESET_MODE_SLEEP: {PHILIPS_POWER: "1", PHILIPS_MODE: "S", PHILIPS_SPEED: "s"},
        PRESET_MODE_TURBO: {PHILIPS_POWER: "1", PHILIPS_MODE: "T", PHILIPS_SPEED: "t"},
    }


class PhilipsAC4236(PhilipsTVOCMixin, PhilipsGenericCoAPFan):
    AVAILABLE_PRESET_MODES = {
        PRESET_MODE_SPEED_1: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "1"},
        PRESET_MODE_SPEED_2: {PHILIPS_POWER: "1", PHILIPS_MODE: "M", PHILIPS_SPEED: "2"},
        PRESET_MODE_AUTO: {PHILIPS_POWER: "1", PHILIPS_MODE: "AG"},
        PRESET_MODE_SLEEP: {PHILIPS_POWER: "1", PHILIPS_MODE: "S", PHILIPS_SPEED: "s"},
        PRESET_MODE_TURBO: {PHILIPS_POWER: "1", PHILIPS_MODE: "T", PHILIPS_SPEED: "t"},
    }
