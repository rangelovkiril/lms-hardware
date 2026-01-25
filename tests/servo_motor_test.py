import sys
import time
from hardware.servo_motor import Servo

def test_servo():
    """
    Real-life hardware tests for Servo class.
    WARNING: Requires a real servo connected to GPIO 18
    and pigpio daemon running.
    """

    print("\n=== SERVO HARDWARE TEST START ===\n")

    # -------------------------------------------------
    # Test 1: Initialization & pigpio connection
    # -------------------------------------------------
    print("[TEST 1] Initializing servo at 90°")
    servo = Servo(angle=90)
    time.sleep(1)
    print("✔ Servo initialized\n")

    # -------------------------------------------------
    # Test 2: Angle mapping (0°, 90°, 180°)
    # -------------------------------------------------
    print("[TEST 2] Testing angle mapping")
    print(" → Moving to 0°")
    servo.set_angle(0)
    time.sleep(1)

    print(" → Moving to 90°")
    servo.set_angle(90)
    time.sleep(1)

    print(" → Moving to 180°")
    servo.set_angle(180)
    time.sleep(1)
    print("✔ Angle mapping test complete\n")

    # -------------------------------------------------
    # Test 3: Bounds checking
    # -------------------------------------------------
    print("[TEST 3] Testing angle bounds")
    try:
        servo.set_angle(-10)
        print("✘ ERROR: No exception for -10°")
    except ValueError:
        print("✔ Correctly rejected -10°")

    try:
        servo.set_angle(200)
        print("✘ ERROR: No exception for 200°")
    except ValueError:
        print("✔ Correctly rejected 200°")
    print()

    # -------------------------------------------------
    # Test 4: Speed-based timing
    # -------------------------------------------------
    print("[TEST 4] Testing speed-based movement timing")
    servo.set_angle(0)
    time.sleep(1)

    start = time.time()
    servo.set_angle(60)  # 60° move
    elapsed = time.time() - start

    print(f" → Movement time: {elapsed:.2f} s (expected ≈ {60/servo._Servo__speed:.2f} s)")
    print("✔ Timing test complete\n")

    # -------------------------------------------------
    # Test 5: Relative rotation
    # -------------------------------------------------
    print("[TEST 5] Testing relative rotation")
    servo.set_angle(90)
    time.sleep(1)

    print(" → Rotate +30° (expect 120°)")
    servo.rotate(30)
    time.sleep(1)

    print(" → Rotate -60° (expect 60°)")
    servo.rotate(-60)
    time.sleep(1)
    print("✔ Relative rotation test complete\n")

    # -------------------------------------------------
    # Test 6: Internal state tracking
    # -------------------------------------------------
    print("[TEST 6] Testing get_angle()")
    servo.set_angle(45)
    time.sleep(0.5)

    angle = servo.get_angle()
    print(f" → get_angle() returned: {angle}")
    if angle == 45:
        print("✔ Angle tracking correct\n")
    else:
        print("✘ Angle tracking incorrect\n")

    # -------------------------------------------------
    # Test 7: Long-term stability
    # -------------------------------------------------
    print("[TEST 8] Long-term stability test")
    for i in range(10):
        servo.set_angle(0)
        servo.set_angle(180)
    print("✔ Stability test complete\n")
    
    # -------------------------------------------------
    # Test 8: Stop PWM output
    # -------------------------------------------------
    print("[TEST 7] Testing servo stop()")
    servo.set_angle(90)
    time.sleep(2)
    servo.set_angle(180)
    time.sleep(2)
    servo.set_angle(90)
    time.sleep(1)

    servo.stop()
    print(" → Servo PWM stopped")
    print(" → Shaft should now move freely by hand")
    time.sleep(2)
    print("✔ Stop test complete\n")


    print("=== SERVO HARDWARE TEST END ===\n")


if __name__ == "__main__":
    test_servo()
