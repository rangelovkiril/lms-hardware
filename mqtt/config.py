from __future__ import annotations

import os
import logging
from dataclasses import dataclass, field
from typing import Optional

log = logging.getLogger(__name__)


@dataclass
class MqttConfig:
    broker_host:   str           = "localhost"
    broker_port:   int           = 1883
    station_id:    str           = "station1"
    obj_id:        str           = "sat1"
    influx_token:  str           = field(default="", repr=False)
    username:      Optional[str] = field(default=None, repr=False)
    password:      Optional[str] = field(default=None, repr=False)
    keepalive:     int           = 60
    reconnect_min: float         = 1.0
    reconnect_max: float         = 30.0
    qos_telemetry: int           = 0
    qos_status:    int           = 1
    qos_cmd:       int           = 1
    publish_hz:    float         = 10.0


def load_config() -> MqttConfig:
    station_id   = _require("STATION_ID")
    obj_id       = _require("OBJ_ID")
    influx_token = _require("INFLUX_TOKEN")

    cfg = MqttConfig(
        broker_host   = os.getenv("MQTT_BROKER",      "localhost"),
        broker_port   = int(os.getenv("MQTT_PORT",    "1883")),
        station_id    = station_id,
        obj_id        = obj_id,
        influx_token  = influx_token,
        username      = os.getenv("MQTT_USER"),
        password      = os.getenv("MQTT_PASSWORD"),
        keepalive     = int(os.getenv("MQTT_KEEPALIVE",  "60")),
        qos_telemetry = int(os.getenv("MQTT_QOS_TEL",    "0")),
        qos_status    = int(os.getenv("MQTT_QOS_STATUS", "1")),
        qos_cmd       = int(os.getenv("MQTT_QOS_CMD",    "1")),
        publish_hz    = float(os.getenv("PUBLISH_HZ",    "10")),
    )

    log.info("[Config] Loaded: broker=%s:%d station=%s obj=%s",
             cfg.broker_host, cfg.broker_port, cfg.station_id, cfg.obj_id)
    log.info("[Config] influx_token present: %s", bool(cfg.influx_token))

    return cfg


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(f"Required environment variable '{key}' is not set.")
    return val
