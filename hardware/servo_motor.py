import pigpio
import time

class Servo:
    """
    Class for controlling a standard PWM servo using pigpio.

    Attributes: 
        __pi: Connection to the pigpio daemon
        __pin: GPIO pin connected to the servo
        __min_us: Minimum PWM pulse width in microseconds
        __max_us: Maximum PWM pulse width in microseconds
        __speed: Maximum servo speed in degrees per second
        __current_angle: Current angle of the servo
    """

    def __init__(self, angle: float, pin: int = 18, min_us: float = 500, max_us: float = 2500, speed: int = 500) -> None:
        """
        Initializes the servo object.
        Args:
            angle (float): Initial servo angle (0–180°)
            pin (int): GPIO pin for controlling the servo (default 18)
            min_us (float): Minimum PWM pulse width in microseconds
            max_us (float): Maximum PWM pulse width in microseconds
            speed (int): Maximum servo speed (degrees/second)
        Raises:
            RuntimeError: If unable to connect to the pigpio daemon
        """
        # Connect to pigpio daemon
        self.__pi = pigpio.pi()
        if not self.__pi.connected:
            raise RuntimeError("Could not connect to pigpio daemon")

        # Servo configuration
        self.__pin: int = pin
        self.__min_us: float = min_us
        self.__max_us: float = max_us
        self.__speed: int = speed
        self.__current_angle: float = 0.0

        # Set initial position
        self.set_angle(angle)

    def __angle_to_pwm(self, angle: float) -> float:
        """
        Converts a servo angle (0–180°) to a PWM pulse width.

        Args:
            angle (float): Target angle

        Returns:
            float: PWM pulse width in microseconds

        Raises:
            ValueError: If the angle is out of bounds
        """
        if angle < 0.0 or angle > 180.0:
            raise ValueError("Angle out of bounds") 

        # Linear mapping: 0° -> min_us, 180° -> max_us
        pwm = self.__min_us + (self.__max_us - self.__min_us) * (angle / 180)
        return pwm

    def set_angle(self, angle: float) -> None:
        """
        Moves the servo to a specific angle, waiting the required
        physical time according to the servo's maximum speed.

        Args:
            angle (float): Target angle (0–180°)
        """
        # Convert angle to PWM signal
        pwm = self.__angle_to_pwm(angle)
        self.__pi.set_servo_pulsewidth(self.__pin, pwm)

        # Calculate physical movement time
        delta_angle = abs(angle - self.__current_angle)
        time.sleep(delta_angle / self.__speed)  # Wait for servo to reach position

        # Update current angle
        self.__current_angle = angle

    def rotate(self, delta: float) -> None:
        """
        Rotates the servo relative to its current position.

        Args:
            delta (float): Change in angle (can be positive or negative)
        """
        self.set_angle(self.__current_angle + delta)

    def get_angle(self) -> float:
        """
        Returns the current angle of the servo.

        Returns:
            float: Current servo angle
        """
        return self.__current_angle

    def stop(self) -> None:
        """
        Stops the servo by setting PWM width to 0 (turns off servo pulse).
        """
        self.__pi.set_servo_pulsewidth(self.__pin, 0)