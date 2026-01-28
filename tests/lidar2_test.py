import time
from hardware.lidar import Lidar
from utils.logger import log


def run_hardware_unit_test():
    print("--- Starting TFmini-S Hardware Unit Test ---")
    try:
        lidar = Lidar(bus_id=3, address=0x10)
        lidar.set_kalman_filter(True)
    except Exception as e:
        print(f"[FAIL] Could not initialize I2C bus: {e}")
        return

    stats = {"total": 100, "success": 0, "checksum_errors": 0, "timeouts": 0}
    distances = []

    print(f"Sampling {stats['total']} frames...")

    for _ in range(stats["total"]):
        if lidar.update():
            data = lidar.get_data()
            if data["distance"] > 0:
                stats["success"] += 1
                distances.append(data["distance"])
        else:
            stats["checksum_errors"] += 1
        time.sleep(0.05)

    # Analysis
    reliability = (stats["success"] / stats["total"]) * 100

    print("\n--- Test Results ---")
    print(f"Reliability: {reliability}%")
    if distances:
        print(f"Avg Distance: {sum(distances)/len(distances):.2f} cm")
        print(f"Min/Max: {min(distances)} / {max(distances)} cm")

    if reliability > 95:
        print("[RESULT] PASS: Sensor is stable.")
    else:
        print("[RESULT] FAIL: High error rate. Check wiring or pull-up resistors.")


if __name__ == "__main__":
    run_hardware_unit_test()
