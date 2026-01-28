from drivers.stepper_motor import StepperMotor


class AzimuthController:
    def __init__(self, gear_ratio=4, arg_microstep=8):
        self.motor = StepperMotor(microstep=arg_microstep)
        self.gear_ratio = gear_ratio

        self.current_angle = 0

        self.steps_per_degree = (
            self.motor.motor_steps_per_rev * self.motor.microstep * self.gear_ratio
        ) / 360

    def move_by_degree(self, delta_degree, delay):
        if delta_degree == 0:
            return

        steps = int(delta_degree * self.steps_per_degree)

        if steps != 0:
            self.motor.enable()
            self.motor.set_direction(clockwise=(steps > 0))

            self.motor.step(abs(steps), delay=delay)

            self.current_angle += delta_degree

    def move_to_angle(self, target_angle, delay):
        delta = target_angle - self.current_angle
        self.move_by_degree(delta, delay)
