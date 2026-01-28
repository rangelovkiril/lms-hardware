import time
from drivers.azimuth_controller import AzimuthController

def test_hardware_precision():
    print("--- Starting Azimuth Hardware Test (Manual Speed Control) ---")
    
    # Initialize without delay parameter in __init__
    az = AzimuthController(gear_ratio=4, arg_microstep=8)
    
    # Define some standard delays (seconds between steps)
    FAST = 0.0005
    SLOW = 0.002
    PRECISION = 0.005

    try:
        print(f"\n[Test 1] Fast move to 90 degrees (Delay: {FAST}s)")
        az.move_to_angle(90, delay=FAST)
        time.sleep(1)

        print(f"[Test 2] Slow return to 0 (Delay: {SLOW}s)")
        az.move_to_angle(0, delay=SLOW)
        time.sleep(1)

        print("\n[Test 3] Variable Speed Increments")
        for i, speed in enumerate([FAST, SLOW, PRECISION]):
            print(f" Step {i+1}: Moving 15° with delay {speed}s")
            az.move_by_degree(15, delay=speed)
            print(f" Current software angle: {az.current_angle}°")
            time.sleep(0.5)

        print("\n[Test 4] Backlash & Precision Check")
        # Moving in small bursts to check for mechanical slip
        az.move_by_degree(5, delay=PRECISION)
        az.move_by_degree(-5, delay=PRECISION)

        print("\n[Test 5] Returning to Absolute Zero (Fast)")
        az.move_to_angle(0, delay=FAST)

    except KeyboardInterrupt:
        print("\nTest stopped by user")
    finally:
        # Crucial: Always disable the motor to prevent heating
        az.motor.disable()
        az.motor.cleanup()
        print("--- Test Finished: Motor Disabled ---")

if __name__ == "__main__":
    test_hardware_precision()