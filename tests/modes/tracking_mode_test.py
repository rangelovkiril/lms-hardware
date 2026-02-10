from core.station import LMSStation
from modes.tracking import track_object
import threading

station = LMSStation()
stop_evt = threading.Event()

try:
    track_object(station=station, stop_event=stop_evt)

finally:
    station.disable()
