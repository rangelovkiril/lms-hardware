import RPi.GPIO as GPIO
import time

class StepperMotor:
    def __init__(self, step_pin=24, dir_pin=25, sleep_pin=23, steps_per_rev=200, start_pos=0):
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.sleep_pin = sleep_pin
        self.steps_per_rev = steps_per_rev
        
        self.position = start_pos
        self.direction = None
        self.enabled = False
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.sleep_pin, GPIO.OUT)
        
        GPIO.output(self.sleep_pin, GPIO.HIGH)
        
    def enable(self):
        GPIO.output(self.sleep_pin, GPIO.HIGH)
        self.enabled = True

    def disable(self):
        GPIO.output(self.sleep_pin, GPIO.LOW)
        self.enabled = False
    
    def set_direction(self, clockwise=True):
        GPIO.output(self.dir_pin, GPIO.HIGH if clockwise else GPIO.LOW)
        self.direction = clockwise

    def step(self, steps=1, delay=0.01):
        for _ in range(steps):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(delay)
            if self.direction:
                self.position = (self.position + 1) % self.steps_per_rev
            else:
                self.position = (self.position - 1) % self.steps_per_rev
    
    def move(self, clockwise, steps, delay=0.01):
        self.enable()
        self.set_direction(clockwise)
        self.step(steps, delay)
        self.disable()
    
    def cleanup(self):
        GPIO.output(self.step_pin, GPIO.LOW)
        GPIO.output(self.sleep_pin, GPIO.LOW)
        GPIO.cleanup([self.step_pin, self.dir_pin])
    
    def get_position(self):
        return self.position

    def go_to(self, target_position, delay=0.01, disable_after=False):
        steps_needed = target_position - self.position
        direction = True if steps_needed >= 0 else False
        self.move(direction, abs(steps_needed), delay)
        if disable_after:
            self.disable()
