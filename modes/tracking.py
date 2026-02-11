import time
from typing import Optional
from utils.logger import log
import threading

from core.station import LMSStation


def track_object(
    station: LMSStation,
    stop_event: Optional[threading.Event] = None,
    el_step: float = 7.0,                  # Degrees to move in elevation
    lidar_detection_threshold: float = 0.3,  # Max range to consider valid (meters)
):
    
    consecutive_misses = 0
    max_misses = 20

    log("INFO", "TRACKING", "Dual-LIDAR gradient tracking started...")

    while not stop_event.is_set():
        
        station.lidar1.update()
        station.lidar2.update()
        
        lidar1_dist = station.lidar1.distance / 100.0
        lidar2_dist = station.lidar2.distance / 100.0
        
        lidar1_valid = (0.01 < lidar1_dist < lidar_detection_threshold)
        lidar2_valid = (0.01 < lidar2_dist < lidar_detection_threshold)
        
        current_az = station.azimuth
        current_el = station.elevation
        
        log(
            "INFO",
            "TRACKING",
            f"L1: {lidar1_dist:.3f}m ({'✓' if lidar1_valid else '✗'}), "
            f"L2: {lidar2_dist:.3f}m ({'✓' if lidar2_valid else '✗'}), "
            f"az={current_az:.2f}°, el={current_el:.2f}°"
        )
        
        el_adjustment = 0.0
        
        if lidar1_valid and lidar2_valid:
            el_adjustment = el_step
            log("INFO", "TRACKING", "Both detect → UP (chasing edge)")
            
        elif lidar1_valid and not lidar2_valid:
            el_adjustment = -el_step
            log("INFO", "TRACKING", "Only L1 → DOWN")
            
        elif lidar2_valid and not lidar1_valid:
            el_adjustment = el_step
            log("INFO", "TRACKING", "Only L2 → UP")
            
        else:
            consecutive_misses += 1
            if consecutive_misses >= max_misses:
                log("INFO", "TRACKING", f"Lost target after {max_misses} attempts")
                return
            log("WARN", "TRACKING", f"No detection ({consecutive_misses}/{max_misses})")
            time.sleep(0.05)
            continue
        
        consecutive_misses = 0
        
        if lidar1_valid and lidar2_valid:
            avg_dist = (lidar1_dist + lidar2_dist) / 2.0
        elif lidar1_valid:
            avg_dist = lidar1_dist
        else:
            avg_dist = lidar2_dist

        target_el = current_el + el_adjustment
        target_el = max(station.el_min, min(target_el, station.el_max))
        
        log(
            "INFO",
            "TRACKING",
            f"el={target_el:.2f}° (Δ{el_adjustment:+.2f}), "
        )
        
        station.move_to(az_angle=station.azimuth, el_angle=target_el, delay=0.0005)
        
        time.sleep(0.05)