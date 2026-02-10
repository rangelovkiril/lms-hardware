"""
Test script to measure LIDAR sensor noise.
Place a stationary object at a fixed distance and run this.
"""

import time
import numpy as np
import sys
import os

from core.station import LMSStation
from utils.logger import log


def test_measurement_noise(num_samples: int = 200, sample_interval: float = 0.02):
    """
    Measure sensor noise by sampling a stationary target.

    Args:
        num_samples: Number of measurements to collect
        sample_interval: Time between samples (seconds)
    """

    log("INFO", "NOISE TEST", "Initializing station...")
    station = LMSStation()

    log("INFO", "NOISE TEST", "=" * 60)
    log("INFO", "NOISE TEST", "MEASUREMENT NOISE TEST")
    log("INFO", "NOISE TEST", "Place a stationary object in front of the sensor")
    log("INFO", "NOISE TEST", f"Will collect {num_samples} samples")
    log("INFO", "NOISE TEST", "=" * 60)

    input("Press ENTER when ready to start...")

    distances = []
    valid_count = 0
    invalid_count = 0

    lidar1_readings = []
    lidar2_readings = []

    log("INFO", "NOISE TEST", "Collecting measurements...")

    for i in range(num_samples):
        detected = station.detect_target()

        if i < 10:
            log(
                "INFO",
                "NOISE TEST",
                f"Sample {i+1}: LIDAR1={station.lidar1.distance/100:.4f}m, "
                f"LIDAR2={station.lidar2.distance/100:.4f}m, "
                f"Detected={detected}, Combined={station.distance:.4f}m",
            )

        lidar1_readings.append(station.lidar1.distance / 100.0)
        lidar2_readings.append(station.lidar2.distance / 100.0)

        if detected and station.distance > 0:
            distances.append(station.distance)
            valid_count += 1

            if (i + 1) % 20 == 0:
                log(
                    "INFO",
                    "NOISE TEST",
                    f"Progress: {i + 1}/{num_samples} samples (valid: {valid_count})",
                )
        else:
            invalid_count += 1

        time.sleep(sample_interval)

    log("INFO", "NOISE TEST", "=" * 60)
    log("INFO", "NOISE TEST", "RAW SENSOR DIAGNOSTICS:")
    log(
        "INFO",
        "NOISE TEST",
        f"LIDAR1 - Mean: {np.mean(lidar1_readings):.4f}m, Std: {np.std(lidar1_readings):.4f}m",
    )
    log(
        "INFO",
        "NOISE TEST",
        f"LIDAR2 - Mean: {np.mean(lidar2_readings):.4f}m, Std: {np.std(lidar2_readings):.4f}m",
    )
    log(
        "INFO",
        "NOISE TEST",
        f"Detection rate: {valid_count}/{num_samples} ({valid_count/num_samples*100:.1f}%)",
    )
    log("INFO", "NOISE TEST", "=" * 60)

    if len(distances) < 10:
        log("ERROR", "NOISE TEST", f"Only {len(distances)} valid measurements!")
        log("ERROR", "NOISE TEST", "Possible issues:")
        log("ERROR", "NOISE TEST", "  1. Object too close or too far (check threshold)")
        log("ERROR", "NOISE TEST", "  2. Object not reflective enough")
        log("ERROR", "NOISE TEST", "  3. LIDAR sensor malfunction")
        log(
            "ERROR",
            "NOISE TEST",
            f"  4. Distance threshold is {station.dist_threshold}m - object might be beyond this",
        )
        station.disable()
        return

    distances = np.array(distances)

    mean_dist = np.mean(distances)
    std_dist = np.std(distances)
    min_dist = np.min(distances)
    max_dist = np.max(distances)

    log("INFO", "NOISE TEST", "=" * 60)
    log("INFO", "NOISE TEST", "RESULTS:")
    log("INFO", "NOISE TEST", f"Valid measurements: {valid_count}/{num_samples}")
    log("INFO", "NOISE TEST", f"Mean distance: {mean_dist:.4f} m")
    log("INFO", "NOISE TEST", f"Std deviation: {std_dist:.4f} m")
    log("INFO", "NOISE TEST", f"Min distance: {min_dist:.4f} m")
    log("INFO", "NOISE TEST", f"Max distance: {max_dist:.4f} m")
    log("INFO", "NOISE TEST", f"Range (max-min): {max_dist - min_dist:.4f} m")
    log("INFO", "NOISE TEST", "=" * 60)

    if std_dist < 0.001:
        log("WARN", "NOISE TEST", "Standard deviation is suspiciously low!")
        log("WARN", "NOISE TEST", "LIDAR might be returning quantized/rounded values")
        log("WARN", "NOISE TEST", "Using conservative estimate: 0.02m")
        recommended_noise = 0.02
    else:
        recommended_noise = std_dist

    log(
        "INFO",
        "NOISE TEST",
        f"RECOMMENDED measurement_noise_std: {recommended_noise:.4f}",
    )
    log("INFO", "NOISE TEST", "=" * 60)

    if std_dist > 0:
        log("INFO", "NOISE TEST", "\nDistance distribution:")
        log(
            "INFO",
            "NOISE TEST",
            f"  Within 1σ: {np.sum(np.abs(distances - mean_dist) <= std_dist) / len(distances) * 100:.1f}%",
        )
        log(
            "INFO",
            "NOISE TEST",
            f"  Within 2σ: {np.sum(np.abs(distances - mean_dist) <= 2*std_dist) / len(distances) * 100:.1f}%",
        )
        log(
            "INFO",
            "NOISE TEST",
            f"  Within 3σ: {np.sum(np.abs(distances - mean_dist) <= 3*std_dist) / len(distances) * 100:.1f}%",
        )

    station.disable()


if __name__ == "__main__":
    test_measurement_noise()
