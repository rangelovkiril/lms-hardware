import time
from hardware.stepper_motor import StepperMotor

def test_stepper():
    motor = StepperMotor()

    print("Initial position:", motor.get_position())

    print("\nEnabling motor...")
    motor.enable()
    print("Motor enabled:", motor.enabled)

    print("\nStepping 10 steps clockwise...")
    motor.set_direction(clockwise=True)
    motor.step(10, delay=0.1)
    print("Position after 10 steps CW:", motor.get_position())

    print("\nStepping 10 steps counter-clockwise...")
    motor.set_direction(clockwise=False)
    motor.step(10, delay=0.1)
    print("Position after 10 steps CCW:", motor.get_position())

    print("\nMoving 10 steps using move() clockwise...")
    motor.move(clockwise=True, steps=10, delay=0.1)
    print("Position after move():", motor.get_position())

    print("\nMoving to absolute position 50...")
    motor.go_to(50, delay=0.1)
    print("Position after go_to(50):", motor.get_position())

    print("\nMoving past full rotation (wrap around)...")
    motor.go_to(250, delay=0.1)
    print("Position after wrapping go_to(250):", motor.get_position())

    print("\nDisabling motor...")
    motor.disable()
    print("Motor enabled:", motor.enabled)

    print("\nCleaning up GPIO...")
    motor.cleanup()
    print("Test complete.")

if __name__ == "__main__":
    test_stepper()
