"""
Test script to estimate process noise.
Move an object smoothly and measure how much actual motion deviates 
from constant velocity assumption.
"""

import time
import numpy as np
import sys
import os

from core.station import LMSStation
from utils.coordinate_conversion import spherical_to_cartesian
from utils.logger import log


def test_process_noise(
    duration: float = 10.0,
    sample_interval: float = 0.05
):
    """
    Estimate process noise by tracking a moving object.
    
    Args:
        duration: How long to track (seconds)
        sample_interval: Time between samples (seconds)
    """
    
    log("INFO", "PROCESS TEST", "Initializing station...")
    station = LMSStation()
    
    log("INFO", "PROCESS TEST", "=" * 60)
    log("INFO", "PROCESS TEST", "PROCESS NOISE TEST")
    log("INFO", "PROCESS TEST", "Move an object smoothly in front of the sensor")
    log("INFO", "PROCESS TEST", f"Will track for {duration} seconds")
    log("INFO", "PROCESS TEST", "=" * 60)
    
    input("Press ENTER when ready to start...")
    
    positions = []
    times = []
    
    log("INFO", "PROCESS TEST", "Tracking... move the object now!")
    
    start_time = time.time()
    
    while (time.time() - start_time) < duration:
        detected = station.detect_target()
        
        if detected and station.distance > 0:
            pos = spherical_to_cartesian(
                station.distance,
                station.azimuth,
                station.elevation
            )
            positions.append(pos)
            times.append(time.time() - start_time)
            
            if len(positions) % 20 == 0:
                log("INFO", "PROCESS TEST", f"Collected {len(positions)} measurements...")
        
        time.sleep(sample_interval)
    
    if len(positions) < 20:
        log("ERROR", "PROCESS TEST", "Not enough valid measurements. Try again.")
        station.disable()
        return
    
    positions = np.array(positions)
    times = np.array(times)
    
    # Compute velocities using finite differences
    velocities = np.diff(positions, axis=0) / np.diff(times)[:, np.newaxis]
    
    # Compute accelerations (change in velocity)
    accelerations = np.diff(velocities, axis=0) / np.diff(times[:-1])[:, np.newaxis]
    
    # Statistics on acceleration (indicates deviation from constant velocity)
    acc_magnitudes = np.linalg.norm(accelerations, axis=1)
    
    mean_acc = np.mean(acc_magnitudes)
    std_acc = np.std(acc_magnitudes)
    max_acc = np.max(acc_magnitudes)
    
    # Estimate process noise based on acceleration
    # Process noise ≈ (1/2) * max_acceleration * dt²
    dt = np.mean(np.diff(times))
    estimated_process_noise = 0.5 * max_acc * (dt ** 2)
    
    log("INFO", "PROCESS TEST", "=" * 60)
    log("INFO", "PROCESS TEST", "RESULTS:")
    log("INFO", "PROCESS TEST", f"Measurements collected: {len(positions)}")
    log("INFO", "PROCESS TEST", f"Mean velocity magnitude: {np.mean(np.linalg.norm(velocities, axis=1)):.4f} m/s")
    log("INFO", "PROCESS TEST", f"Mean acceleration: {mean_acc:.4f} m/s²")
    log("INFO", "PROCESS TEST", f"Std acceleration: {std_acc:.4f} m/s²")
    log("INFO", "PROCESS TEST", f"Max acceleration: {max_acc:.4f} m/s²")
    log("INFO", "PROCESS TEST", "=" * 60)
    log("INFO", "PROCESS TEST", f"RECOMMENDED process_noise_std (conservative): {estimated_process_noise:.4f}")
    log("INFO", "PROCESS TEST", f"RECOMMENDED process_noise_std (aggressive): {estimated_process_noise * 2:.4f}")
    log("INFO", "PROCESS TEST", "=" * 60)
    log("INFO", "PROCESS TEST", "Note: Start with conservative value and increase if filter is too slow")
    
    station.disable()


if __name__ == "__main__":
    test_process_noise()