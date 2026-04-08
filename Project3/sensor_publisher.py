# sensor_publisher.py
# Project 4: Grand Marina MQTT Publisher
#
# What this script does:
# - Pretends to be one HYDROLOGIC device in the main building
# - Generates realistic-ish water readings every 2 seconds
# - Publishes them to MQTT as JSON
# - Prints each reading so you can screenshot proof it’s sending

import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


class WaterSensorMQTT:
    """
    Water sensor that publishes readings to an MQTT broker.

    I’m keeping device_id and location in the payload because:
    - device_id = which sensor (identity / serial)
    - location = where it’s installed (helps routing + dashboards)
    """

    def __init__(self, device_id: str, location: str, broker: str = "localhost", port: int = 1883):
        self.device_id = device_id
        self.location = location
        self.counter = 0

        # Base values so the numbers don't look random-random
        self.base_pressure_up = 82.0
        self.base_pressure_down = 76.0
        self.base_flow = 40.0

        # Topic the instructions require
        self.topic = f"hydroficient/grandmarina/sensors/{self.location}/readings"

        # MQTT client setup
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        # Connect once, then start the network loop in the background
        self.client.connect(broker, port)
        self.client.loop_start()

    def _utc_iso_timestamp(self) -> str:
        # ISO 8601 UTC timestamp
        return datetime.now(timezone.utc).isoformat()

    def get_reading(self) -> dict:
        """
        Make a single reading with realistic variation.
        Each call increments the counter.
        """
        self.counter += 1

        pressure_up = round(self.base_pressure_up + random.uniform(-2, 2), 1)
        pressure_down = round(self.base_pressure_down + random.uniform(-2, 2), 1)
        flow_rate = round(self.base_flow + random.uniform(-3, 3), 1)

        return {
            "device_id": self.device_id,
            "location": self.location,
            "timestamp": self._utc_iso_timestamp(),
            "counter": self.counter,
            "pressure_upstream": pressure_up,
            "pressure_downstream": pressure_down,
            "flow_rate": flow_rate,
        }

    def publish_reading(self) -> dict:
        """
        Generate a reading and publish it as JSON.
        Returns the reading so we can print it to the terminal.
        """
        reading = self.get_reading()
        payload = json.dumps(reading)

        # QoS 0 is fine for routine readings (matches the lesson)
        self.client.publish(self.topic, payload, qos=0)
        return reading

    def run_continuous(self, interval_seconds: int = 2) -> None:
        """
        Publish readings forever every interval_seconds.
        Ctrl+C to stop.
        """
        print(f"Starting device: {self.device_id}")
        print(f"Location: {self.location}")
        print(f"Publishing to: {self.topic}")
        print(f"Interval: {interval_seconds} seconds")
        print("-" * 40)

        try:
            while True:
                reading = self.publish_reading()

                # Print format matches the expected output style
                print(
                    f"[{reading['counter']}] "
                    f"Pressure: {reading['pressure_upstream']}/{reading['pressure_downstream']} PSI, "
                    f"Flow: {reading['flow_rate']} gal/min"
                )

                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print("\nSensor stopped.")
        finally:
            # Clean shutdown so Mosquitto logs look normal
            self.client.loop_stop()
            self.client.disconnect()


if __name__ == "__main__":
    # The instructions want main-building specifically for this part
    sensor = WaterSensorMQTT(device_id="GM-HYDROLOGIC-01", location="main-building")
    sensor.run_continuous(interval_seconds=2)
