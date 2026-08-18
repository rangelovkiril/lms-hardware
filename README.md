# lms-hardware

Python controller for the hardware side of a distributed Satellite Laser Ranging (SLR) station. It runs on a Raspberry Pi, drives the pointing mechanism (a stepper motor for azimuth, a PWM servo for elevation), reads four TFmini-S lidar units over I2C, and reports telemetry over MQTT.

The station is commanded remotely rather than locally: the process connects to an MQTT broker, subscribes to a command topic, and waits. On a `track` command it runs a grid scan to acquire the target, then switches to a closed loop that keeps the target centered using differential lidar readings, publishing position samples while it does. The software counterpart, which owns the broker, the InfluxDB time series, and the Next.js 3D visualization, lives in [lms-controller](https://github.com/rangelovkiril/lms-controller). This repository contains only the code that runs on the station itself.

## Running

`main.py` is the entry point. It parses two arguments, `--mock` and `--log-level`, loads a `.env` file if `python-dotenv` is installed, configures logging, and builds an `MqttConfig` from the environment.

- Default (hardware) run: constructs `LMSStation`, which initializes the four lidars, the azimuth controller, and the servo, wraps it in a `StationController`, connects to the broker, and blocks until interrupted. The controller registers two command handlers, `track` and `stop`, and executes the locate and tracking modes on a background thread.
- `--mock` run: skips hardware entirely. It connects to the broker and publishes synthetic position, environment, and log messages every two seconds, which exercises the MQTT path without a station attached.

`load_config()` requires `STATION_ID`, `OBJ_ID`, and `INFLUX_TOKEN` to be present in the environment and raises if any is missing. Everything else has a default: `MQTT_BROKER` (localhost), `MQTT_PORT` (1883), `MQTT_USER`, `MQTT_PASSWORD`, `MQTT_KEEPALIVE`, the three QoS levels, and `PUBLISH_HZ` (10).

Topics are namespaced per station as `slr/<STATION_ID>/...`: the client subscribes to `cmd` and publishes to `status`, `env`, `log/<LEVEL>`, and `tracking/<OBJ_ID>/pos`. Command payloads are JSON objects with an `action` field, which the dispatcher maps to a registered handler.

> [!WARNING]
> `requirements.txt` is a full `pip freeze` of the Raspberry Pi system image, so it carries OS packages and several hundred `types-*` stubs. It also omits three imports the code actually needs: `paho-mqtt`, `numpy`, and `python-dotenv`. It is not usable as a clean dependency list.

## Stack

- Python 3, standard library `threading` for the operating loops
- `paho-mqtt` (MQTT v5) for the command and telemetry link
- `smbus2` for I2C access to the TFmini-S lidars
- `RPi.GPIO` for the stepper driver pins, `pigpio` for servo PWM
- `numpy` for the coordinate conversion helpers

Hardware defaults, taken from the driver constructors: lidars at address `0x10` on I2C buses 1, 3, 4, and 5; stepper on BCM pins 24 (step), 25 (direction), 23 (sleep), 20 and 21 (microstep select); servo on BCM pin 18 with a 500 to 2500 microsecond pulse range. Elevation is clamped to 30 to 150 degrees.

## Project structure

```
main.py       entry point, argument parsing, mock and hardware paths
core/         LMSStation, the hardware facade (movement, lidar reads, target detection)
drivers/      TFmini-S lidar, stepper motor, azimuth controller, servo
modes/        locate (serpentine grid scan) and tracking (differential lidar correction)
mqtt/         config, paho client, command dispatcher, station controller
utils/        spherical and cartesian conversion, logging helper
tests/        standalone bring-up scripts per driver, plus noise measurement scripts
```

> [!NOTE]
> `tests/` holds hardware bring-up and measurement scripts run directly against a connected station, not an automated suite. There is no test runner configured and most of them require the physical hardware.

Licensed under GPL-3.0.
