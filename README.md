[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

This is a `Local Push` integration for Philips airpurifiers.
Currently only encrypted-CoAP is implemented.

## BREAKING CHANGE:

Change of platform name from philips_airpurifier to philips_airpurifier_coap to allow parallel operation of http custom component

## Install:

Add `https://github.com/betaboon/philips-airpurifier.git` as custom-repository in [HACS](https://hacs.xyz/docs/faq/custom_repositories/)


## Setup:

### Single device

Add the following to your `configuration.yaml`:

```yaml
fan:
  platform: philips_airpurifier_coap
  host: 192.168.0.17
  model: ac4236
```

*adapt the `host` according to your setup*

### Multiple devices

Add the following to your `configuration.yaml`:

```yaml
fan:
  - platform: philips_airpurifier_coap
    host: 192.168.0.100
    model: ac1214

  - platform: philips_airpurifier_coap
    host: 192.168.0.101
    model: ac1214

  - platform: philips_airpurifier_coap
    host: 192.168.0.102
    model: ac1214
```

*adapt the `host` according to your setup*


## Configuration variables:
Field | Value | Necessity | Description
--- | --- | --- | ---
platform | `philips_airpurifier_coap` | *Required* | The platform name.
host | 192.168.0.17 | *Required* | IP address of the Purifier.
model | ac4236 | *Required* | Model of the Purifier.
name | Philips Air Purifier | Optional | Name of the Fan.
***


## Supported models:

- AC1214
- AC2729
- AC2889
- AC2939
- AC3059
- AC3829
- AC3858
- AC4236
- AC5659

## Is your model not supported yet?

You can help to get us there.

Please open an issue and provide the raw status-data for each combination of modes and speeds for your model.

To aquire those information please follow these steps:

### Prepare the environment

```sh
git clone https://github.com/betaboon/philips-airpurifier.git
cd philips-airpurifier
source aioairctrl-shell.sh
```

### Aquire raw status-data

- Use the philips-app to activate a mode or speed
- run the following command to aquire the raw data (still in the venv)

```sh
aioairctrl --host $DEVICE_IP status --json
```

## Debugging:

To aquire debug-logs, add the following to your `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.philips_airpurifier_coap: debug
    coap: debug
    aioairctrl: debug
```

logs should now be available in `home-assistant.log`


## Usage:

The integration provides `fan` entities for your devices which are [documented here](https://www.home-assistant.io/integrations/fan/).

### Services:

`philips_airpurifier_coap` registers the following services in addition to the standard `fan`services:

#### Turn the child lock on

```yaml
service: set_child_lock_on
data:
  entity_id: fan.ac2729_bedroom
```

#### Turn the child lock off

```yaml
service: set_child_lock_off
data:
  entity_id: fan.ac2729_bedroom
```

#### Turn the display backlight on

```yaml
service: set_display_backlight_on
data:
  entity_id: fan.ac2729_bedroom
```

#### Turn the display backlight off

```yaml
service: set_display_backlight_off
data:
  entity_id: fan.ac2729_bedroom
```

#### Set the light brightness

```yaml
service: set_light_brightness
data:
  entity_id: fan.ac2729_bedroom
  brightness: 50
```

Brightness can take values between 0 and 100

#### Set function of the device

```yaml
service: set_function
data:
  entity_id: fan.ac2729_bedroom
  function: purification
```

This only applies to devices which offer purification and humidification. The `function` can take the values of `purification` or `purification_humidification`.

#### Set humidity target

```yaml
service: set_humidity_target
data:
  entity_id: fan.ac2729_bedroom
  humidity_target: 50
```

This only applies to devices which offer humidification. The `humidity_target` can take the values of `40`, `50`, `60`, or `70`.


### Attributes

The available attributes depend on the model. The following list gives an overview:

| attribute |content | example |
|---|---|---|
| preset_modes: | Available operating modes of current device | `1`, `2`, `3`, `allergen`, `auto`, `night`, `turbo` |
| preset_mode: | State of operating mode | auto |
| name: | Name of the device | bedroom |
| type: | Configured model | AC2729 |
| model_id: | Philips model ID | AC2729/10 |
| product_id: | Philips product ID | 85bc26fae62611e8a1e3061302926720 |
| device_id: | Philips device ID | 3c84c6c8123311ebb1ae8e3584d00715 |
| software_version: | Installed software version on device | 0.2.1 |
| wifi_version: | Installed WIFI version on device | AWS_Philips_AIR\@62.1 |
| error_code: | Philips error code | 49408 |
| error: | Error in clear text | no water |
| child_lock: | State of child lock setting | false |
| light_brightness: | State of brightness level | 50 |
| display_backlight: | State of display backlight | false |
| preferred_index: | State of preferred air quality index | `PM2.5`, `IAI` |
| filter_pre_remaining: | Time until pre-filter needs cleaning in readable text | 10 days, 23:00:00 |
| filter_pre_remaining_raw: | Time until pre-filter needs cleaning in hours | 263 |
| filter_hepa_type: | Type of installed HEPA filter | A3 |
| filter_hepa_remaining: | Time until HEPA filter needs replacement in readable text | 47 days, 14:00:00 |
| filter_hepa_remaining_raw: | Time until HEPA filter needs replacement in hours | 1142 |
| filter_active_carbon_type: | Type of installed active carbon filter | C7 |
| filter_active_carbon_remaining: | Time until active carbon filter needs replacement in readable text | 47 days, 14:00:00 |
| filter_active_carbon_remaining_raw: | Time until active carbon filter needs replacement in hours | 1142 |
| runtime: | Time the device is running in readable text | 9 days, 10:44:41 |
| air_quality_index: | State of Air Quality Index | 4 |
| indoor_allergen_index: | State of Indoor Allergen Index | 2 |
| pm25: | State of PM2.5 measurement | 8 |
| filter_wick_remaining: | Time until wick filter needs clearning in readable text | 47 days, 14:00:00 |
| filter_wick_remaining_raw: | Time until wick filter needs cleaning in hours | 1142 |
| function: | State of operating function | Purification
| humidity: | State of humidity in percent | 40 |
| humidity_target: | Set of target humidity in percent | 50 |
| temperature: | State of temperature in degrees Celsius | 20 |
| water_level: | State of water level in tank in percent | 50 |
| friendly_name: | Configured name for device | Bedroom |
| icon: | Configured icon | pap:fan_speed_button |
| supported_features: | Supported features | 8 |