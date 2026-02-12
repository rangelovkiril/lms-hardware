import time
from typing import Optional
from utils.logger import log
import threading

from core.station import LMSStation


def compute_elevation_adjustment(
    lidar1_dist: float,
    lidar2_dist: float,
    detection_threshold: float,
    el_step: float,
):
    lidar1_valid = 0.01 < lidar1_dist < detection_threshold
    lidar2_valid = 0.01 < lidar2_dist < detection_threshold

    if lidar1_valid and lidar2_valid:
        return el_step
    elif lidar1_valid and not lidar2_valid:
        return -el_step
    elif lidar2_valid and not lidar1_valid:
        return el_step
    else:
        return None


def handle_miss(consecutive_misses: int, max_misses: int):
    consecutive_misses += 1
    log(
        "WARN",
        "ELEVATION TRACKING",
        f"No detection ({consecutive_misses}/{max_misses})",
    )
    lost = consecutive_misses >= max_misses
    return consecutive_misses, lost


def track_elevation(
    station: LMSStation,
    lidar_lock: threading.Lock,
    shared_data: dict,
    stop_event: threading.Event,
    el_step: float = 7.0,
    lidar_detection_threshold: float = 0.3,
):
    consecutive_misses = 0
    max_misses = 20

    log("INFO", "ELEVATION TRACKING", "Elevation tracking thread started")

    while not stop_event.is_set():
        with lidar_lock:
            lidar1_dist, lidar2_dist = station.read_lidars()
            shared_data.update(
                {
                    "lidar1_dist": lidar1_dist,
                    "lidar2_dist": lidar2_dist,
                    "timestamp": time.time(),
                }
            )

        current_el = station.elevation

        el_adjustment = compute_elevation_adjustment(
            lidar1_dist, lidar2_dist, lidar_detection_threshold, el_step
        )

        if el_adjustment is None:
            consecutive_misses, lost_target = handle_miss(
                consecutive_misses, max_misses
            )

            if lost_target:
                log("ERROR", "ELEVATION TRACKING", "Lost target")
                stop_event.set()
                return

            time.sleep(0.05)
            continue

        consecutive_misses = 0

        target_el = current_el + el_adjustment
        target_el = max(station.el_min, min(target_el, station.el_max))

        log(
            "INFO",
            "ELEVATION TRACKING",
            f"Move EL: {current_el:.2f}° → {target_el:.2f}°",
        )

        station.move_elevation(target_el)

        time.sleep(0.005)


def track_object(
    station: LMSStation,
    stop_event: Optional[threading.Event] = None,
    el_step: float = 3.0,
    lidar_detection_threshold: float = 0.2,
):
    if stop_event is None:
        stop_event = threading.Event()

    lidar_lock = threading.Lock()
    shared_data = {"lidar1_dist": 0.0, "lidar2_dist": 0.0, "timestamp": 0.0}

    el_thread = threading.Thread(
        target=track_elevation,
        args=(
            station,
            lidar_lock,
            shared_data,
            stop_event,
            el_step,
            lidar_detection_threshold,
        ),
        name="ElevationTracking",
        daemon=True,
    )

    log("INFO", "TRACKING", "Starting tracking...")
    el_thread.start()

    try:
        el_thread.join()
    except KeyboardInterrupt:
        log("INFO", "TRACKING", "Stopping tracking...")
        stop_event.set()
        el_thread.join(timeout=2.0)

    log("INFO", "TRACKING", "Tracking stopped")
