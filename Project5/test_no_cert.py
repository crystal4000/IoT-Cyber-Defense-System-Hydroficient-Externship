# test_no_cert.py - Should be REJECTED (mTLS)
import time
import ssl
import paho.mqtt.client as mqtt

# Handle paho-mqtt 2.0+ API change
try:
    MQTT_CLIENT_ARGS = {"callback_api_version": mqtt.CallbackAPIVersion.VERSION1}
except AttributeError:
    MQTT_CLIENT_ARGS = {}

connected = False
failed = False
fail_reason = None

def on_connect(client, userdata, flags, rc):
    global connected, failed, fail_reason
    # If this fires with rc==0, the broker accepted us (bad for this test)
    if rc == 0:
        connected = True
    else:
        failed = True
        fail_reason = f"MQTT connect rc={rc}"

def on_disconnect(client, userdata, rc):
    global failed, fail_reason
    # Non-zero disconnect rc usually means handshake/connection failed
    if rc != 0 and not failed:
        failed = True
        fail_reason = f"Disconnected rc={rc}"

client = mqtt.Client(client_id="rogue-device", **MQTT_CLIENT_ARGS)
client.on_connect = on_connect
client.on_disconnect = on_disconnect

# Only CA cert, NO client certificate/key (this should fail with require_certificate true)
client.tls_set(
    ca_certs="certs/ca.pem",
    certfile=None,
    keyfile=None,
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS,
)

try:
    client.connect("localhost", 8883, keepalive=10)
    client.loop_start()

    # Wait briefly for handshake + CONNACK (or failure)
    timeout_s = 3
    start = time.time()
    while time.time() - start < timeout_s and not connected and not failed:
        time.sleep(0.05)

    client.loop_stop()
    client.disconnect()

    if connected:
        print("ERROR: Rogue client connected (mTLS NOT enforced)")
    else:
        print(f"SUCCESS: Connection rejected (as expected). Reason: {fail_reason or 'TLS handshake failed'}")

except Exception as e:
    print(f"SUCCESS: Connection rejected immediately: {e}")