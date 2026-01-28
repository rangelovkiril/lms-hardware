import time
from core.station import LMSStation


def run_stress_test():
    print("🚀 Starting LMS Hardware Stress & Sweep Test")

    # Init with very fast defaults
    station = LMSStation(threshold=0.4, step_delay=0.0005)

    try:
        # TEST 1: The "Homing" Sweep
        # Sweeps azimuth while checking sensors to find the 'edge' of your desk/room
        print("\n[Phase 1] Rapid Azimuth Sweep & Sensor Sync")
        sweep_points = [-45, 0, 45, 0]
        for point in sweep_points:
            print(f"  -> Sweeping to {point}°...")
            # We poll sensors WHILE moving to stress the CPU/I2C
            station.move_to(az_angle=point, el_angle=90)
            found = station.detect_target()
            print(f"  Current: {station.azimuth}° | Target Found: {found}")

        # TEST 2: Multi-Axis "Circle"
        # Checks if the Servo and Stepper interfere with each other's power draw
        print("\n[Phase 2] High-Torque Multi-Axis Stress")
        for i in range(3):
            print(f"  Cycle {i+1}: Snapping to Extremes")
            # Move to bottom-left fast
            station.move_to(-30, 10, delay=0.0003)
            # Move to top-right slow (precision)
            station.move_to(30, 170, delay=0.005)
            time.sleep(0.2)

        # TEST 3: Infinite Detection Loop (Manual verification)
        print("\n[Phase 3] Live Tracking View (Ctrl+C to stop)")
        print(f"{'Azimuth':>8} | {'Elevation':>8} | {'Dist':>8} | {'Status'}")
        print("-" * 50)

        while True:
            locked = station.detect_target()
            status = "!! TARGET !!" if locked else "scanning..."

            # Print on one line using carriage return \r
            output = f"{station.azimuth:>8.1f}° | {station.elevation:>8.1f}° | {station.distance:>8.3f}m | {status}"
            print(output, end="\r")
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\n🛑 Test stopped by user.")
    finally:
        print("Cleaning up hardware...")
        station.az_actuator.motor.disable()
        station.az_actuator.motor.cleanup()
        station.servo.stop()
        print("Done.")


if __name__ == "__main__":
    run_stress_test()
