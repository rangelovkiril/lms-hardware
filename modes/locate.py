import time
import math
from typing import Optional, Dict, Iterator
from utils.logger import log
import threading

from core.station import LMSStation


def scan_grid(
    az_min: float,
    az_max: float,
    az_step: float,
    el_min: float,
    el_max: float,
    el_step: float,
    serpentine: bool = True,
) -> Iterator[Dict[str, float]]:

    az_values = []
    if az_step == 0:
        az_values = [az_min]
    else:
        a = az_min
        while (a <= az_max + 1e-9 and az_step > 0) or (
            a >= az_max - 1e-9 and az_step < 0
        ):
            az_values.append(round(a, 6))
            a += az_step

    el_values = []
    if el_step == 0:
        el_values = [el_min]
    else:
        e = el_min
        while (e <= el_max + 1e-9 and el_step > 0) or (
            e >= el_max - 1e-9 and el_step < 0
        ):
            el_values.append(round(e, 6))
            e += el_step

    for i, el in enumerate(el_values):
        if serpentine and (i % 2 == 1):
            az_iter = reversed(az_values)
        else:
            az_iter = iter(az_values)
        for az in az_iter:
            yield {"az": az, "el": el}


def locate_target(
    station: LMSStation,
    az_min: float = -90.0,
    az_max: float = 90.0,
    az_step: float = 5.0,
    el_min: float = 20.0,
    el_max: float = 40.0,
    el_step: float = 10.0,
    dwell: float = 0.05,
    timeout: Optional[float] = 30.0,
    stop_event: Optional[threading.Event] = None,
    incremental_az_step: float = 2.0,
    servo_wait_timeout: float = 1.0,
    servo_tolerance_deg: float = 0.5,
) -> Optional[dict]:

    start_t = time.time()
    stop_event = stop_event or threading.Event()
    deadline = start_t + timeout if timeout is not None else None

    el_min = max(el_min, station.el_min)
    el_max = min(el_max, station.el_max)

    grid = scan_grid(az_min, az_max, az_step, el_min, el_max, el_step, serpentine=True)

    for point in grid:
        if stop_event.is_set() or (deadline and time.time() > deadline):
            return None

        target_az = point["az"]
        target_el = point["el"]

        station.move_elevation(
            target_el, tolerance_deg=servo_tolerance_deg, timeout=servo_wait_timeout
        )

        found = station.move_azimuth_incremental(
            target_az=target_az,
            step=incremental_az_step,
            dwell=dwell,
            stop_event=stop_event,
            timeout_deadline=deadline,
            on_poll=lambda: station.detect_target() and station.distance > 0,
        )

        if found:
            return station.log_target_found()

    return None
