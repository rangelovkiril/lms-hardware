import unittest
from unittest.mock import patch
from drivers.stepper_motor import StepperMotor, SAFE_MICROSTEP


class TestStepperMotor(unittest.TestCase):
    def setUp(self):
        # Print test name and description before each test
        print(f"\nRunning test: {self._testMethodName} - {self._testMethodDoc}")

    @patch("hardware.stepper_motor.log")
    @patch("hardware.stepper_motor.GPIO")
    def test_microstep_invalid_fallback(self, mock_gpio, mock_log):
        """Ensure invalid microstep falls back to SAFE_MICROSTEP and logs a warning"""
        motor = StepperMotor(motor_steps_per_rev=200, microstep=1)  # valid first
        motor.set_microstepping_state(5)  # invalid → triggers log
        self.assertEqual(motor.microstep, SAFE_MICROSTEP)
        mock_log.assert_called_once()

    @patch("hardware.stepper_motor.GPIO")
    def test_enable_disable(self, mock_gpio):
        """Enable and disable should set GPIO and update enabled state"""
        motor = StepperMotor(motor_steps_per_rev=200)
        motor.enable()
        mock_gpio.output.assert_any_call(motor.sleep_pin, mock_gpio.HIGH)
        self.assertTrue(motor.enabled)

        motor.disable()
        mock_gpio.output.assert_any_call(motor.sleep_pin, mock_gpio.LOW)
        self.assertFalse(motor.enabled)

    @patch("hardware.stepper_motor.GPIO")
    def test_set_direction(self, mock_gpio):
        """Set direction should set GPIO pin correctly and update direction attribute"""
        motor = StepperMotor(motor_steps_per_rev=200)
        motor.set_direction(clockwise=True)
        mock_gpio.output.assert_any_call(motor.dir_pin, mock_gpio.HIGH)
        self.assertTrue(motor.direction)

        motor.set_direction(clockwise=False)
        mock_gpio.output.assert_any_call(motor.dir_pin, mock_gpio.LOW)
        self.assertFalse(motor.direction)

    @patch("hardware.stepper_motor.GPIO")
    @patch("hardware.stepper_motor.time.sleep", return_value=None)
    def test_step_position_increment(self, mock_sleep, mock_gpio):
        """Stepping should correctly increment/decrement position depending on direction"""
        motor = StepperMotor(motor_steps_per_rev=200, microstep=2)
        motor.set_direction(clockwise=True)
        motor.step(steps=4, delay=0)
        self.assertEqual(motor.position, 4 % motor.steps_per_rev)

        motor.set_direction(clockwise=False)
        motor.step(steps=2, delay=0)
        expected = (4 - 2) % motor.steps_per_rev
        self.assertEqual(motor.position, expected)

    @patch("hardware.stepper_motor.GPIO")
    def test_cleanup(self, mock_gpio):
        """Cleanup should set pins low and call GPIO.cleanup"""
        motor = StepperMotor(motor_steps_per_rev=200)
        motor.cleanup()
        mock_gpio.output.assert_any_call(motor.step_pin, mock_gpio.LOW)
        mock_gpio.output.assert_any_call(motor.sleep_pin, mock_gpio.LOW)
        mock_gpio.cleanup.assert_called_once_with([motor.step_pin, motor.dir_pin])


# Custom runner to print results in terminal clearly
class VerboseTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        print(f"[SUCCESS] {test._testMethodName}: {test._testMethodDoc}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        print(f"[FAILED] {test._testMethodName}: {test._testMethodDoc}")

    def addError(self, test, err):
        super().addError(test, err)
        print(f"[ERROR] {test._testMethodName}: {test._testMethodDoc}")


if __name__ == "__main__":
    runner = unittest.TextTestRunner(resultclass=VerboseTestResult, verbosity=0)
    unittest.main(testRunner=runner, exit=False)
