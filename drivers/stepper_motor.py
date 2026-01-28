import RPi.GPIO as GPIO
import time
from utils.logger import log

SAFE_MICROSTEP = 1


class StepperMotor:
    def __init__(
        self,
        step_pin=24,
        dir_pin=25,
        sleep_pin=23,
        ms1_pin=20,
        ms2_pin=21,
        motor_steps_per_rev=200,
        start_pos=0,
        microstep=1,
    ):
        """
        Initializes GPIO pins and sets the initial microstepping resolution.

        Args:
            step_pin (int): BCM pin for the STEP signal.
            dir_pin (int): BCM pin for the DIRECTION signal.
            sleep_pin (int): BCM pin for the SLEEP/ENABLE signal.
            ms1_pin (int): BCM pin for microstep selection bit 1.
            ms2_pin (int): BCM pin for microstep selection bit 2.
            motor_steps_per_rev (int): Native steps of the motor (usually 200).
            start_pos (int): Initial step count for tracking.
            microstep (int): Desired microstepping divisor (1, 2, 4, or 8).
        """

        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.sleep_pin = sleep_pin
        self.ms1_pin = ms1_pin
        self.ms2_pin = ms2_pin

        self.motor_steps_per_rev = motor_steps_per_rev
        self.microstep = microstep
        self.steps_per_rev = motor_steps_per_rev

        self.position = start_pos
        self.direction = True
        self.enabled = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.ms1_pin, GPIO.OUT)
        GPIO.setup(self.ms2_pin, GPIO.OUT)
        GPIO.setup(self.sleep_pin, GPIO.OUT)

        GPIO.output(self.sleep_pin, GPIO.LOW)
        self.set_microstepping_state(microstep)

    def set_microstepping_state(self, state):
        """
        Configures the A4988 MS1 and MS2 pins for a specific resolution.
        Updates the internal steps_per_rev to ensure position tracking
        remains accurate relative to the new step size.

        Args:
            state (int): The microstepping divisor.
                         Must be one of {1, 2, 4, 8}.
                         1 = Full step, 8 = 1/8 step.
        """

        if state not in microstepping_states:
            log(
                "WARN",
                "STEPPER",
                f"Invalid microstep state: {state} → fallback to {SAFE_MICROSTEP}",
            )
            state = SAFE_MICROSTEP
        ms1_val, ms2_val = microstepping_states[state]
        GPIO.output(self.ms1_pin, ms1_val)
        GPIO.output(self.ms2_pin, ms2_val)
        self.steps_per_rev = self.motor_steps_per_rev * state
        self.microstep = state

    def enable(self):
        """
        Energizes the motor coils by setting the sleep pin HIGH,
        so it stops being in sleep mode.
        Required before calling step().
        """
        GPIO.output(self.sleep_pin, GPIO.HIGH)
        self.enabled = True

    def disable(self):
        """
        De-energizes the motor coils to save power and prevent overheating.
        """
        GPIO.output(self.sleep_pin, GPIO.LOW)
        self.enabled = False

    def set_direction(self, clockwise=True):
        """
        Sets the rotation direction for subsequent steps.

        Args:
            clockwise (bool): True for CW rotation, False for CCW.
        """
        GPIO.output(self.dir_pin, GPIO.HIGH if clockwise else GPIO.LOW)
        self.direction = clockwise

    def step(self, steps=1, delay=0.01):
        """
        Generates a series of PWM pulses to move the motor.

        Updates the 'position' attribute based on the number of pulses
        and the current direction.

        Args:
            steps (int): Number of steps to move.
            delay (float): Seconds between pulse states (controls speed).
        """
        for _ in range(steps):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(delay)

            if self.direction:
                self.position = (self.position + 1) % self.steps_per_rev
            else:
                self.position = (self.position - 1) % self.steps_per_rev

    def cleanup(self):
        """
        Resets GPIO pins to a safe state and releases control.
        Should be called during system shutdown.
        """
        GPIO.output(self.step_pin, GPIO.LOW)
        GPIO.output(self.sleep_pin, GPIO.LOW)
        GPIO.cleanup([self.step_pin, self.dir_pin])


microstepping_states = {1: (0, 0), 2: (1, 0), 4: (0, 1), 8: (1, 1)}
