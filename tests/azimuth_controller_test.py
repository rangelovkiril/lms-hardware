import time
from drivers.azimuth_controller import AzimuthController


def test_hardware_precision():
    print("--- Starting Azimuth Hardware Test ---")
    # Инициализираме с твоите параметри
    az = AzimuthController(gear_ratio=4, arg_microstep=8, arg_delay=0.0002)

    try:
        print("Test 1: Moving to 90 degrees...")
        az.move_to_angle(90)
        time.sleep(1)

        print("Test 2: Moving back to 0...")
        az.move_to_angle(0)
        time.sleep(1)

        print("Test 3: Moving 5 times by 10 degrees...")
        for i in range(5):
            az.move_by_degree(10)
            print(f" Current software angle: {az.current_angle}°")
            time.sleep(0.2)

        print("Test 4: Backlash check (10 deg right, 10 deg left)...")
        az.move_by_degree(10)
        az.move_by_degree(-10)

        print("Test 5: Returning to Absolute Zero...")
        az.move_to_angle(0)

    except KeyboardInterrupt:
        print("\nTest stopped by user")
    finally:
        az.motor.disable()
        az.motor.cleanup()
        print("--- Test Finished: Motor Disabled ---")


if __name__ == "__main__":
    test_hardware_precision()
