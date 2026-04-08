# dashboard_subscriber.py
# Project 4: Grand Marina MQTT Subscriber (Dashboard)
#
# What this script does:
# - Connects to the local Mosquitto broker
# - Subscribes to hydroficient/grandmarina/# so it sees EVERYTHING for the hotel
# - Tries to parse incoming messages as JSON (sensor readings)
# - Prints a clean, dashboard-style view for humans
# - If the message is not JSON, it prints it as raw text instead of crashing

import json
from datetime import datetime

import paho.mqtt.client as mqtt


def print_header() -> None:
    print("\n" + "=" * 60)
    print("  GRAND MARINA WATER MONITORING DASHBOARD")
    print("  Connected at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)


def display_reading(data: dict) -> None:
    """
    Formats one sensor reading and checks for simple alert thresholds.
    """

    location = data.get("location", "Unknown")
    device_id = data.get("device_id", "Unknown")
    timestamp = data.get("timestamp", "N/A")
    counter = data.get("counter", 0)

    up = data.get("pressure_upstream", 0)
    down = data.get("pressure_downstream", 0)
    flow = data.get("flow_rate", 0)

    try:
        diff = float(up) - float(down)
    except (TypeError, ValueError):
        diff = 0.0

    # --- Basic Threshold Checks ---
    alerts = []

    if up > 90:
        alerts.append("HIGH UPSTREAM PRESSURE")

    if down < 65:
        alerts.append("LOW DOWNSTREAM PRESSURE")

    if flow > 60:
        alerts.append("HIGH FLOW RATE - POSSIBLE LEAK")

    if flow < 20:
        alerts.append("LOW FLOW RATE - POSSIBLE BLOCKAGE")

    # --- Display Section ---
    print("\n" + "─" * 40)
    print(f"  Location:  {location}")
    print(f"  Device ID: {device_id}")
    print(f"  Time:      {timestamp}")
    print(f"  Count:     #{counter}")
    print("─" * 40)

    # Show alerts if any
    if alerts:
        print("  *** ALERTS ***")
        for alert in alerts:
            print(f"  >>> {alert}")
        print("─" * 40)

    print(f"  Pressure (upstream):   {up:>6} PSI")
    print(f"  Pressure (downstream): {down:>6} PSI")
    print(f"  Flow rate:             {flow:>6} gal/min")
    print(f"  Pressure differential: {diff:>6.1f} PSI")

def on_connect(client, userdata, flags, reason_code, properties):
    # reason_code == 0 means the connection succeeded
    if reason_code == 0:
        print_header()
        client.subscribe("hydroficient/grandmarina/#")
    else:
        print(f"Failed to connect. reason_code={reason_code}")


def on_message(client, userdata, msg):
    topic = msg.topic
    raw_payload = msg.payload.decode(errors="replace")

    # Try JSON first (sensor readings are JSON in this project)
    try:
        data = json.loads(raw_payload)

        # Only format as a sensor reading if it looks like one
        # This helps if we later publish alerts/commands/status that are also JSON.
        if isinstance(data, dict) and "pressure_upstream" in data and "flow_rate" in data:
            display_reading(data)
        else:
            # JSON but not a sensor-reading shape, so show it without crashing
            print(f"\n[JSON] {topic}")
            print(f"      {raw_payload}")

    except json.JSONDecodeError:
        # Not JSON at all, print as raw text
        print(f"\n[RAW] {topic}")
        print(f"      {raw_payload}")


def main():
    print("Connecting to broker...")

    # Callback API v2 to match the project doc
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    # Local broker (Mosquitto) default port
    client.connect("localhost", 1883)

    # Blocks forever, waiting for messages
    client.loop_forever()


if __name__ == "__main__":
    main()
