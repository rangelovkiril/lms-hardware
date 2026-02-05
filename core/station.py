from typing import Optional, Callable
import threading
import time
from drivers.lidar import Lidar
from drivers.azimuth_controller import AzimuthController
from drivers.servo_motor import Servo
from utils.logger import log


class LMSStation:
    def __init__(
        self,
        gear_ratio: int = 4,
        microstep: int = 8,
        step_delay: float = 0.005,
        threshold: float = 0.2,
        el_min: float = 10,
        el_max: float = 170,
    ) -> None:

        self.gear_ratio: int = gear_ratio
        self.microstep: int = microstep
        self.step_delay: float = step_delay
        self.dist_threshold: float = threshold

        self.el_min: float = el_min
        self.el_max: float = el_max

        self.distance: float = 0.0
        self.elevation: float = el_min
        self.azimuth: float = 0.0

        self.lidar1: Lidar = Lidar(bus_id=1, address=0x10)
        self.lidar2: Lidar = Lidar(bus_id=3, address=0x10)

        self.az_actuator: AzimuthController = AzimuthController(
            gear_ratio=self.gear_ratio, arg_microstep=self.microstep
        )

        self.servo: Servo = Servo(angle=self.elevation)

        log(
            "INFO",
            "STATION",
            f"LMS Station initialized. Threshold: {self.dist_threshold}m, El Limits: [{self.el_min}, {self.el_max}]",
        )

    def detect_target(self) -> bool:
        self.lidar1.update()
        self.lidar2.update()

        d1: float = self.lidar1.distance / 100.0
        d2: float = self.lidar2.distance / 100.0

        valid_points: list[float] = []
        for d in [d1, d2]:
            if 0.01 < d < self.dist_threshold and d != 655.35:
                valid_points.append(d)

        if valid_points:
            self.distance = sum(valid_points) / len(valid_points)
            return True

        self.distance = 0.0
        return False

    def move_to(
        self, az_angle: float, el_angle: float, delay: Optional[float] = None
    ) -> None:

        move_delay: float = delay if delay is not None else self.step_delay

        self.az_actuator.move_to_angle(az_angle, delay=move_delay)

        clamped_el: float = max(self.el_min, min(el_angle, self.el_max))
        self.servo.set_angle(clamped_el)

        self.azimuth = self.az_actuator.current_angle
        self.elevation = self.servo.get_angle()

    def move_azimuth_incremental(
        self,
        target_az: float,
        step: float,
        dwell: float,
        stop_event: threading.Event,
        timeout_deadline: Optional[float] = None,
        on_poll: Optional[Callable[[], bool]] = None,
    ) -> bool:

        current_az: float = self.az_actuator.current_angle
        self.azimuth = current_az

        remaining: float = target_az - current_az

        while abs(remaining) > 1e-6:
            if stop_event.is_set():
                return False
            if timeout_deadline is not None and time.time() > timeout_deadline:
                return False

            step_signed: float = step if remaining > 0 else -step
            if abs(step_signed) > abs(remaining):
                step_signed = remaining

            try:
                self.az_actuator.move_by_degree(step_signed, delay=self.step_delay)
            except Exception as e:
                log("ERROR", "STATION", f"Incremental azimuth move failed: {e}")
                return False

            current_az = self.az_actuator.current_angle
            self.azimuth = current_az

            poll_start: float = time.time()
            while (time.time() - poll_start) < max(dwell, 0.02):
                if stop_event.is_set():
                    return False
                if timeout_deadline is not None and time.time() > timeout_deadline:
                    return False

                if on_poll is not None:
                    try:
                        if on_poll():
                            return True
                    except Exception:
                        pass

                time.sleep(max(self.step_delay, 0.01))

            remaining = target_az - current_az
            time.sleep(0.001)

        if on_poll is not None:
            try:
                return bool(on_poll())
            except Exception:
                pass

        return False

    def disable(self) -> None:
        self.az_actuator.disable()
        self.servo.stop()
        self.lidar1.close()
        self.lidar2.close()
        log("INFO", "STATION", f"LMS Station disabled")