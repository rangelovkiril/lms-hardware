from core.station import LMSStation
from modes.tracking import track_object
from modes.locate import locate_target
import threading
import time

station = LMSStation(threshold=1.0)
stop_evt = threading.Event()

try:
    station.servo.set_angle(0)
    time.sleep(1)
    found = locate_target(
        station,
        az_min=-5,
        az_max=5,
        az_step=5,
        el_min=30,
        el_max=40,
        el_step=2,
        dwell=0.0005,
        timeout=20.0,
        stop_event=stop_evt,
    )
    if found:
        track_object(
            station=station, stop_event=stop_evt, lidar_detection_threshold=1.0
        )

finally:
    station.disable()
