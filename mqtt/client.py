from __future__ import annotations

import json
import logging
import threading
from typing import Optional

import paho.mqtt.client as paho
from paho.mqtt.client import MQTTMessage, MQTTv5, MQTT_CLEAN_START_FIRST_ONLY

from .config     import MqttConfig
from .dispatcher import CommandDispatcher

log = logging.getLogger(__name__)


class StationMqttClient:

    def __init__(self, config: MqttConfig) -> None:
        self.cfg        = config
        self.dispatcher = CommandDispatcher()
        self._connected = threading.Event()

        self._client = paho.Client(
            client_id=f"slr-{config.station_id}",
            protocol=MQTTv5,
            clean_session=None,
        )

        if config.username:
            self._client.username_pw_set(config.username, config.password)

        self._client.will_set(
            topic=self._topic("status"),
            payload=json.dumps({"event": "offline"}),
            qos=config.qos_status,
            retain=True,
        )

        self._client.on_connect    = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message    = self._on_message
        self._client.on_subscribe  = self._on_subscribe

    def _topic(self, suffix: str) -> str:
        return f"slr/{self.cfg.station_id}/{suffix}"

    def connect(self) -> None:
        self._client.connect(
            self.cfg.broker_host,
            self.cfg.broker_port,
            keepalive=self.cfg.keepalive,
            clean_start=MQTT_CLEAN_START_FIRST_ONLY,
        )
        self._client.loop_start()
        if not self._connected.wait(timeout=10.0):
            log.warning("[MQTT] Не се свърза в рамките на 10 s – ще опитва отново")

    def disconnect(self) -> None:
        try:
            self.publish_status("offline")
        except Exception:
            pass
        self._client.loop_stop()
        self._client.disconnect()
        log.info("[MQTT] Disconnected")

    def wait_connected(self, timeout: float = 30.0) -> bool:
        return self._connected.wait(timeout=timeout)

    @property
    def is_connected(self) -> bool:
        return self._connected.is_set()

    def _on_connect(self, client, userdata, flags, rc, properties=None) -> None:
        if rc != 0:
            log.error("[MQTT] Connection refused – rc=%s", rc)
            return
        log.info("[MQTT] Свързан към %s:%d", self.cfg.broker_host, self.cfg.broker_port)
        self._connected.set()
        client.subscribe(self._topic("cmd"), qos=self.cfg.qos_cmd)
        log.info("[MQTT] Абониран за %s", self._topic("cmd"))
        self.publish_status("online")

    def _on_disconnect(self, client, userdata, rc, properties=None) -> None:
        self._connected.clear()
        if rc == 0:
            log.info("[MQTT] Clean disconnect")
        else:
            log.warning("[MQTT] Неочакван disconnect rc=%s – Paho ще reconnect-не", rc)

    def _on_message(self, client, userdata, msg: MQTTMessage) -> None:
        topic = msg.topic
        raw   = msg.payload.decode("utf-8", errors="replace")
        log.debug("[MQTT] ← %s  %s", topic, raw)
        if not topic.endswith("/cmd"):
            return
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            log.error("[MQTT] Невалиден JSON на %s: %r", topic, raw)
            return
        self.dispatcher.dispatch(payload)

    def _on_subscribe(self, client, userdata, mid, granted_qos, properties=None) -> None:
        log.debug("[MQTT] Subscription confirmed mid=%s qos=%s", mid, granted_qos)

    def _publish(self, topic: str, payload: dict | str, qos: int, retain: bool = False) -> None:
        if isinstance(payload, dict):
            payload = json.dumps(payload)
        result = self._client.publish(topic, payload, qos=qos, retain=retain)
        if result.rc != paho.MQTT_ERR_SUCCESS:
            log.error("[MQTT] Publish грешка на %s rc=%s", topic, result.rc)

    def publish_status(self, event: str, **kwargs) -> None:
        payload: dict = {"event": event, **kwargs}
        self._publish(
            topic=self._topic("status"),
            payload=payload,
            qos=self.cfg.qos_status,
            retain=(event in ("online", "offline")),
        )
        log.info("[MQTT] → status  %s", payload)

    def publish_position(self, obj_id: str, az: float, el: float, dist: float) -> None:
        payload = {
            "az":           round(az,   6),
            "el":           round(el,   6),
            "dist":         round(dist, 6),
            "influx_token": self.cfg.influx_token,
        }
        self._publish(self._topic(f"tracking/{obj_id}/pos"), payload, qos=self.cfg.qos_telemetry)
        log.debug("[MQTT] → pos  az=%.2f el=%.2f dist=%.2f", az, el, dist)

    def publish_env(self, fields: dict[str, float]) -> None:
        self._publish(self._topic("env"), fields, qos=self.cfg.qos_telemetry)
        log.debug("[MQTT] → env  %s", fields)

    def publish_log(self, level: str, message: str) -> None:
        self._publish(
            topic=self._topic(f"log/{level.upper()}"),
            payload=message,
            qos=self.cfg.qos_telemetry,
        )
        log.debug("[MQTT] → log/%s  %s", level.upper(), message)
