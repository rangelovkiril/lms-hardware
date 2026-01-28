import time
from drivers.stepper_motor import StepperMotor, SAFE_MICROSTEP


def test_stepper():
    print("\n=== REAL-LIFE STEPPER MOTOR TESTS ===")

    print("\nTest 1: Invalid microstep fallback")
    motor = StepperMotor(motor_steps_per_rev=200, microstep=5)  # invalid → fallback
    print(f"Initial position: {motor.position}, microstep: {motor.microstep}")
    if motor.microstep == SAFE_MICROSTEP:
        print("[PASS] Microstep fallback worked")
    else:
        print("[FAIL] Microstep fallback did not work")

    print("\nTest 2: Enable motor")
    motor.enable()
    print(f"Motor enabled: {motor.enabled}")
    print("[PASS]" if motor.enabled else "[FAIL]")

    print("\nTest 3: Step forward 400 microsteps")
    motor.set_direction(clockwise=True)
    motor.step(400, delay=0.005)
    print(f"Position after forward steps: {motor.position}")
    expected_pos = 400 % motor.steps_per_rev
    print("[PASS]" if motor.position == expected_pos else "[FAIL]")

    print("\nTest 4: Step backward 200 microsteps")
    motor.set_direction(clockwise=False)
    motor.step(700, delay=0.005)
    print(f"Position after backward steps: {motor.position}")
    expected_pos = (expected_pos - 200) % motor.steps_per_rev
    print("[PASS]" if motor.position == expected_pos else "[FAIL]")

    print("\nTest 5: Direction changes")
    motor.set_direction(clockwise=True)
    print(f"Direction set to clockwise: {motor.direction}")
    motor.set_direction(clockwise=False)
    print(f"Direction set to counter-clockwise: {motor.direction}")
    print("[PASS]" if motor.direction == False else "[FAIL]")

    print("\nTest 6: Disable and cleanup")
    motor.disable()
    print(f"Motor enabled after disable: {motor.enabled}")
    motor.cleanup()
    print("Cleanup done")
    print("[PASS]" if not motor.enabled else "[FAIL]")

    print("\n=== REAL-LIFE TESTS COMPLETE ===")


if __name__ == "__main__":
    test_stepper()
