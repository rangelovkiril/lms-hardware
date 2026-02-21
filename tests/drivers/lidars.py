import time
from drivers.lidar import Lidar
from drivers.azimuth_controller import AzimuthController
from utils.logger import log


def run_hardware_unit_test():
    print("--- Starting TFmini-S Hardware Unit Test ---")
    try:
        lidar = Lidar(bus_id=1, address=0x10)
        lidar2 = Lidar(bus_id=3, address=0x10)
        c = AzimuthController(gear_ratio=4, arg_microstep=8)
        lidar.set_kalman_filter(False)
    except Exception as e:
        print(f"[FAIL] Could not initialize I2C bus: {e}")
        return

    try:
        while True:
            c.move_by_degree(1, 0.002)
            lidar.update()
            lidar2.update()
            data1 = lidar.get_data()
            data2 = lidar2.get_data()
            print(f"l1 = {data1['distance']}, l2 = {data2['distance']}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        lidar.close()
        lidar2.close()
        print("Test stopped, buses closed")


if __name__ == "__main__":
    run_hardware_unit_test()
