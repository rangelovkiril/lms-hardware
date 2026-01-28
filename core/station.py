from drivers.lidar import Lidar
from drivers.azimuth_controller import AzimuthController
from drivers.servo_motor import Servo
from utils.logger import log


class LMSStation:
    def __init__(
        self,
        gear_ratio=4,
        microstep=8,
        step_delay=0.005,
        threshold=0.2,
        el_min=10,
        el_max=170,
    ):

        self.gear_ratio = gear_ratio
        self.microstep = microstep
        self.step_delay = step_delay
        self.dist_threshold = threshold

        self.el_min = el_min
        self.el_max = el_max

        self.distance = 0.0
        self.elevation = el_min
        self.azimuth = 0.0

        self.lidar1 = Lidar(bus_id=1, address=0x10)
        self.lidar2 = Lidar(bus_id=3, address=0x10)

        self.az_actuator = AzimuthController(
            gear_ratio=self.gear_ratio, arg_microstep=self.microstep
        )

        self.servo = Servo(angle=self.elevation)

        log(
            "INFO",
            "STATION",
            f"LMS Station initialized. Threshold: {self.dist_threshold}m, El Limits: [{self.el_min}, {self.el_max}]",
        )

    def detect_target(self):
        self.lidar1.update()
        self.lidar2.update()

        d1 = self.lidar1.distance / 1000.0
        d2 = self.lidar2.distance / 1000.0

        valid_points = []
        for d in [d1, d2]:
            if 0.01 < d < self.dist_threshold and d != 655.35:
                valid_points.append(d)

        if valid_points:
            self.distance = sum(valid_points) / len(valid_points)
            return True

        self.distance = 0.0
        return False

    def move_to(self, az_angle, el_angle, delay=None):

        move_delay = delay if delay is not None else self.step_delay

        self.az_actuator.move_to_angle(az_angle, delay=move_delay)

        clamped_el = max(self.el_min, min(el_angle, self.el_max))
        self.servo.set_angle(clamped_el)

        self.azimuth = self.az_actuator.current_angle
        self.elevation = self.servo.get_angle()
