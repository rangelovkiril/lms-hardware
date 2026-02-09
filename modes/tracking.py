import time
import numpy as np
from typing import Optional, Dict, Iterator
from utils.logger import log
import threading
import filterpy

from core.station import LMSStation
from utils.coordinate_conversion import spherical_to_cartesian


def track_object(
    station: LMSStation,
    stop_event: Optional[threading.Event] = None,
):
    while not stop_event.is_set():
        detected = station.detect_target()
        if not detected:
            continue

        theta = station.azimuth  # horizontal
        phi = station.elevation  # vertical
        cur_dist = station.distance
        state_vector = spherical_to_cartesian(
            dist=cur_dist, azimuth_deg=theta, elevation_deg=phi
        )

        log(
            "INFO",
            "TRACKING ROUTINE",
            f"STATE VECTOR COORINATES: x = {state_vector[0]}; y = {state_vector[1]}; z = {state_vector[2]}",
        )

        time.sleep(0.01)
