from encodings.base64_codec import base64_decode

from mqtt.client import create_client
from canbus.dbc_loader import load_dbc
from influxDB.writer import InfluxDBWriter
from canbus.parser import decode_can_message
import struct
import config

dbc1 = load_dbc(config.DBC.get("file1"))
dbc3 = load_dbc(config.DBC.get("file3"))
writer = InfluxDBWriter()


def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connected")
    else:
        print("Connection failed")
    client.subscribe(config.MQTT.get("topic"))


# TODO: Check dbccpp package, figure out why this is necessary in C++
def on_message(client, userdata, msg):
    data = base64_decode(msg.payload)
    print(f"Received message on topic {msg.topic}")
    print(f"Raw payload: {msg.payload}")
    for offset in range(0, len(data) - 17 + 1, 17):
        arbitration = ((data[offset] << 8) | data[offset + 1]) & 0x7FF
        can_bus = data[offset + 4] >> 4
        dlc = data[offset + 4] & 0x0F
        can_data = data[offset + 5: offset + 5 + dlc]
        timestamp = struct.unpack(">i", data[offset + 13:offset + 17])[0]
        print(f"arbitration:{arbitration}")
        print(f"can_bus:{can_bus}")
        print(f"dlc:{dlc}")
        print(f"can_data:{can_data}")
        print(f"timestamp:{timestamp}")
        if can_bus == 0:
            dbc = dbc1
        else:
            dbc = dbc3

        # Verify this
        msg_name, signals = dbc.decode_message(arbitration, can_data)
        print(f"Message: {msg_name}({arbitration})")
        print(f"Signals: {signals}")

        if signals:
            writer.write(msg_name, f"canbus{can_bus}", signals, timestamp)


client = create_client(on_connect, on_message)
client.username_pw_set(config.MQTT.get("username"), config.MQTT.get("password"))
client.connect(config.MQTT.get("host"), config.MQTT.get("port"), 10)
client.loop_forever()
