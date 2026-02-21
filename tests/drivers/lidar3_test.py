import time
from drivers.lidar import Lidar
from drivers.azimuth_controller import AzimuthController
from utils.logger import log


def run_hardware_unit_test():
    print("--- Starting TFmini-S Hardware Unit Test ---")
    try:
        lidar = Lidar(bus_id=5, address=0x10)
        c = AzimuthController(gear_ratio=4, arg_microstep=8)
        lidar.set_kalman_filter(False)
    except Exception as e:
        print(f"[FAIL] Could not initialize I2C bus: {e}")
        return

    try:
        while True:
            lidar.update()
            data1 = lidar.get_data()
            print(f"l1 = {data1['distance']}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        lidar.close()
        print("Test stopped, buses closed")


if __name__ == "__main__":
    run_hardware_unit_test()
