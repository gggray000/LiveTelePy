from datetime import datetime, timedelta
from pkg_resources import SOURCE_DIST
import pytz
from messages.types import *
import cantools

class MessageParser:

    def __init__(self, dbc_paths: List[str]):
        self.db = cantools.db.load_file(dbc_paths[0])
        if len(dbc_paths) >= 1:
            for path in dbc_paths:
                # Reference: https://github.com/cantools/cantools/issues/58
                self.db.add_dbc_file(path)

    def convert_mqtt_to_can(self, received: MqttMessage) -> List[CanMessage]:
        payload_len = 17
        mqtt_msgs = []
        payloads = [received.payload[i:i + payload_len] for i in range(0, len(received.payload), payload_len)]
        for payload in payloads:
            mqtt_msg = received.copy()
            mqtt_msg.payload = payload
            mqtt_msgs.append(mqtt_msg)

        can_msgs = []
        for mqtt_msg in mqtt_msgs:
            can_msg = CanMessage()
            timestamp = (int.from_bytes(mqtt_msg.payload[13:17],'little'))/1000
            print(timestamp)
            base_time = datetime(2025, 6, 16, 0, 0, 0, tzinfo=pytz.utc)
            #current_time = datetime.now(pytz.utc).replace(hour=21, minute=0, second=0, microsecond=0)
            print(base_time)
            can_msg.timestamp = base_time + timedelta(seconds=timestamp)
            print(can_msg.timestamp)
            can_msg.msg_id = int.from_bytes(mqtt_msg.payload[0:4], 'little')
            can_msg.dlc = int.from_bytes(mqtt_msg.payload[4:5], 'little')
            can_msg.can_bus = can_msg.dlc >> 4
            can_msg.dlc &= 15
            can_msg.data = mqtt_msg.payload[5:13]

            can_msgs.append(can_msg)

        return can_msgs

    def decode_can_message(self, can_msgs: List[CanMessage]) -> List[InfluxMessage]:
        influx_msgs = []
        for can_msg in can_msgs:
            try:
                decoded = self.db.get_message_by_frame_id(can_msg.msg_id)
                influx_msg = InfluxMessage()
                influx_msg.name = decoded.name
                influx_msg.signals = decoded.decode(can_msg.data)
                influx_msg.timestamp = can_msg.timestamp
                print(influx_msg.timestamp)
                influx_msgs.append(influx_msg)
                
            except Exception as e:
                print(f"[CAN] Failed to decode ID {can_msg.msg_id}: {e}")
                continue

        return influx_msgs

        
