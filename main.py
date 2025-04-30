import base64
from base64 import b64decode

# from encodings.base64_codec import base64_decode

from mqtt.client import create_client
from canbus.dbc_loader import load_dbc
from influxDB.writer import InfluxDBWriter
from canbus.parser import decode_can_message
import struct
import config

dbc1 = load_dbc(config.DBC.get("file1"))
dbc3 = load_dbc(config.DBC.get("file3"))
print(f"DBC1 version:{dbc1.nodes}")
print(f"DBC3 version:{dbc3.nodes}")
writer = InfluxDBWriter()


def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connected")
    else:
        print("Connection failed")
    client.subscribe(config.MQTT.get("topic"))

def on_message(client, userdata, msg):
    data = b64decode(msg.payload)
    print(f"Received message on topic {msg.topic}")
    print(f"Raw payload: {msg.payload}\n")
    for offset in range(0, len(data) - 17 + 1, 17):
        arbitration = ((data[offset] << 8) | data[offset + 1]) & 0x7FF
        can_bus = data[offset + 4] >> 4
        dlc = data[offset + 4] & 0x0F
        can_data = data[offset + 5: offset + 5 + dlc]
        timestamp = struct.unpack(">i", data[offset + 13:offset + 17])[0]

        print(f"arbitration:{arbitration}")
        print(f"can_bus:{can_bus}")
        print(f"dlc:{dlc}")
        print(f"can_data:{can_data.hex()}")
        print(f"timestamp:{timestamp}")

        if can_bus not in (0, 1):
            print(f"Skipping unknown CAN bus {can_bus}")

        if can_bus == 0:
            dbc = dbc1
        else:
            dbc = dbc3

        if arbitration in dbc._frame_id_to_message:
            msg_name, signals = dbc.decode_message(arbitration, can_data)
            print(f"Message: {msg_name}({arbitration})")
            print(f"Signals: {signals}")
            writer.write(msg_name, f"canbus{can_bus}", signals, timestamp)
        else:
            print(f"Unknown arbitration ID: {arbitration}\n")

client = create_client(on_connect, on_message)
client.username_pw_set(config.MQTT.get("username"), config.MQTT.get("password"))
client.connect(config.MQTT.get("host"), config.MQTT.get("port"), 10)
client.loop_forever()
