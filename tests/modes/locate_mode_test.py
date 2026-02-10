from core.station import LMSStation
from modes.locate import locate_target
import threading

station = LMSStation()
stop_evt = threading.Event()

try:
    found = locate_target(
        station,
        az_min=-5,
        az_max=5,
        az_step=5,
        el_min=10,
        el_max=20,
        el_step=2,
        dwell=0.0005,
        timeout=20.0,
        stop_event=stop_evt,
    )
    if found:
        print("Found target")
    else:
        print("No target found")

finally:
    station.disable()
