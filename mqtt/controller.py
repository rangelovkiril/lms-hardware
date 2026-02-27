from __future__ import annotations

import logging
import threading
import time
from typing import Optional

from .client import StationMqttClient
from .config import MqttConfig

log = logging.getLogger(__name__)


class StationController:

    def __init__(self, station, config: MqttConfig) -> None:
        from modes.locate   import locate_target
        from modes.tracking import track_object

        self._station    = station
        self._locate     = locate_target
        self._track      = track_object
        self._obj_id     = config.obj_id
        self._publish_hz = config.publish_hz
        self.mqtt        = StationMqttClient(config)

        self._op_thread:      Optional[threading.Thread] = None
        self._publish_thread: Optional[threading.Thread] = None
        self._stop_event:     Optional[threading.Event]  = None

        self.mqtt.dispatcher.register("track", self._cmd_track)
        self.mqtt.dispatcher.register("stop",  self._cmd_stop)

    def _cmd_track(self, payload: dict) -> None:
        self._stop_current()
        self._stop_event = threading.Event()
        stop   = self._stop_event
        obj_id = self._obj_id

        def _publish_loop() -> None:
            interval = 1.0 / self._publish_hz
            while not stop.is_set():
                az   = self._station.azimuth
                el   = self._station.elevation
                dist = self._station.distance
                if dist > 0:
                    self.mqtt.publish_position(obj_id, az, el, dist)
                time.sleep(interval)

        def _run() -> None:
            self._station.enable()

            try:
                self.mqtt.publish_log("INFO", f"Locate scan started for {obj_id}")

                result = None
                try:
                    result = self._locate(self._station, stop_event=stop)
                except Exception as exc:
                    log.exception("[CTRL] locate_target raised: %s", exc)

                if stop.is_set():
                    self.mqtt.publish_log("INFO", "Locate cancelled")
                    return

                if not result:
                    self.mqtt.publish_log("WARN", f"Target not found for {obj_id}")
                    self.mqtt.publish_status("tracking_stop")
                    return

                self.mqtt.publish_log(
                    "INFO",
                    f"Target acquired: az={result['az']:.2f} "
                    f"el={result['el']:.2f} dist={result['range_m']:.3f}",
                )

                self.mqtt.publish_status("tracking_start", objId=obj_id)

                self._publish_thread = threading.Thread(
                    target=_publish_loop, name="PublishLoop", daemon=True
                )
                self._publish_thread.start()

                try:
                    self._track(self._station, stop_event=stop)
                except Exception as exc:
                    log.exception("[CTRL] track_object raised: %s", exc)
                finally:
                    stop.set()
                    self.mqtt.publish_status("tracking_stop")
                    self.mqtt.publish_log("INFO", f"Tracking stopped for {obj_id}")

            finally:
                self._station.az_actuator.disable()

        self._op_thread = threading.Thread(target=_run, name="TrackThread", daemon=True)
        self._op_thread.start()

    def _cmd_stop(self, payload: dict) -> None:
        self._stop_current()
        self.mqtt.publish_log("INFO", "Station stopped by command")

    def _stop_current(self) -> None:
        if self._stop_event:
            self._stop_event.set()
        if self._op_thread and self._op_thread.is_alive():
            self._op_thread.join(timeout=5.0)
        if self._publish_thread and self._publish_thread.is_alive():
            self._publish_thread.join(timeout=2.0)
        self._op_thread      = None
        self._publish_thread = None
        self._stop_event     = None

    def start(self) -> None:
        self.mqtt.connect()
        self._station.az_actuator.disable()
        log.info("[CTRL] Station controller running. Press Ctrl+C to quit.")
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self) -> None:
        self._stop_current()
        self._station.disable()
        self.mqtt.disconnect()
