import base64
from base64 import b64decode
from mqtt.client import create_client
from canbus.dbc_loader import load_dbc
from influxDB.writer import InfluxDBWriter
import config
from cantools.database.errors import DecodeError

# Load DBCs
dbc1 = load_dbc(config.DBC.get("file1"))
dbc3 = load_dbc(config.DBC.get("file3"))
print(f"DBC1 version:{dbc1.nodes}")
print(f"DBC3 version:{dbc3.nodes}")

# Writer instance
writer = InfluxDBWriter(config.INFLUX)

# MQTT connect callback
def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connected")
    else:
        print("Connection failed")
    client.subscribe(config.MQTT.get("topic"))

# MQTT message callback
def on_message(client, userdata, msg):
    data = msg.payload
    print(f"Received message on topic {msg.topic}")
    print(f"Raw payload: {msg.payload}\n")

    for offset in range(0, len(data) - 17 + 1, 17):
        arbitration = ((data[offset] << 8) | data[offset + 1]) & 0x7FF
        can_bus = data[offset + 4] >> 4
        dlc = data[offset + 4] & 0x0F
        can_data = data[offset + 5: offset + 5 + dlc]
        timestamp = (
            (data[offset + 13] << 24) |
            (data[offset + 14] << 16) |
            (data[offset + 15] << 8) |
            data[offset + 16]
        )

        print(f"arbitration: {arbitration}")
        print(f"can_bus: {can_bus}")
        print(f"dlc: {dlc}")
        print("can_data:", " ".join(f"{byte:02x}" for byte in can_data))
        print(f"timestamp: {timestamp}")

        if can_bus not in (0, 1):
            print(f"Skipping unknown CAN bus {can_bus}")
            continue

        dbc = dbc1 if can_bus == 0 else dbc3

        msg_def = dbc._frame_id_to_message.get(arbitration)
        if not msg_def:
            print(f"Unknown arbitration ID: {arbitration}\n")
            continue

        if len(can_data) < msg_def.length:
            print(f"Warning: Skipping ID {arbitration} due to short data: {len(can_data)} < expected {msg_def.length}")
            continue

        try:
            signals = msg_def.decode(can_data, allow_truncated=True)
            print(f"Message: {msg_def.name} ({arbitration})")
            print(f"Signals: {signals}")
            writer.write(msg_def.name, f"canbus{can_bus}", signals, timestamp)
        except DecodeError as e:
            print(f"Failed to decode arbitration ID {arbitration}: {e}")

# Setup and run MQTT client
client = create_client(on_connect, on_message)
client.username_pw_set(config.MQTT.get("username"), config.MQTT.get("password"))
client.connect(config.MQTT.get("host"), config.MQTT.get("port"), 10)
client.loop_forever()