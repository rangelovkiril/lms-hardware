import argparse
import logging
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from mqtt import load_config, StationMqttClient, StationController


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    )

    config = load_config()

    if args.mock:
        _run_mock(config)
    else:
        _run_hardware(config)


def _run_mock(config) -> None:
    log = logging.getLogger("mock")
    client = StationMqttClient(config)
    client.connect()
    client.wait_connected(timeout=10)
    log.info("Mock loop started – Ctrl+C to stop")
    try:
        i = 0
        while True:
            client.publish_position("sat_mock", az=float(i * 10 % 360), el=30.0 + i % 60, dist=400.0 + i)
            client.publish_env({"temperature": 22.0 + i * 0.1, "humidity": 55.0})
            client.publish_log("INFO", f"Mock tick {i}")
            i += 1
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()


def _run_hardware(config) -> None:
    from core.station import LMSStation
    station = LMSStation()
    ctrl    = StationController(station, config)
    ctrl.start()


if __name__ == "__main__":
    main()
