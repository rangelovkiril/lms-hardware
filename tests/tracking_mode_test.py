from core.station import LMSStation
from modes.tracking import track_object
import threading

station = LMSStation()
stop_evt = threading.Event()

try:
    station.lidar1.set_kalman_filter(active=False)
    station.lidar2.set_kalman_filter(active=False)
    station.move_to(az_angle=20, el_angle=40)
    track_object(station=station, stop_event=stop_evt)

finally:
    station.disable()
