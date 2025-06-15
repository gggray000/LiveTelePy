import argparse
import base64
import json

from typing import List
from influxDB.writer import InfluxdbConfig, InfluxDBWriter
from messages.types import MqttMessage
from parser.parser import MessageParser
import config
import urllib3

# TODO: Resolve SSL issue
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

dbcs: List[str] = [config.DBC.get("file1"), config.DBC.get("file2"), config.DBC.get("file3")]
messageParser = MessageParser(dbcs)

influx_config = InfluxdbConfig(
    config.INFLUX_REPLAY.get("token"),
    config.INFLUX_REPLAY.get("org"),
    config.INFLUX_REPLAY.get("url"),
    config.INFLUX_REPLAY.get("bucket")
)

writer = InfluxDBWriter(influx_config)

def main(json_path, mqtt_msg=None):
    with open(json_path, 'r') as f:
        clients = json.load(f)

    for client in clients:
        messages = client.get("messages", [])
        for msg in messages:
            payload_base64 = msg.get("payload") or msg.get("properties", {}).get("payload")
            if not payload_base64:
                print("No payload found in messages, skipping.")
                continue

            try:
                print("\nRaw payload: " + payload_base64)
                payload_bytes = base64.b64decode(payload_base64)
                print("\nPayload after base64 decoding: ")
                print(payload_bytes)
                print(f"\nPayload contains messages: {len(payload_bytes)/17}")

                mock_mqtt_msg = MqttMessage(
                    payload=payload_bytes,
                    topic=msg.get("topic", ""),
                    timestamp=msg.get("timestamp", 0)
                )

                influx_msgs = messageParser.decode_can_message(
                    messageParser.convert_mqtt_to_can(mock_mqtt_msg)
                )
                writer.write(influx_msgs)

                for influx_msg in influx_msgs:
                    print(influx_msg)

            except Exception as e:
                print(f"Failed to process payload: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write logged MQTT messages to InfluxDB from a JSON file")
    parser.add_argument("json_path", help="Path to the JSON file")
    args = parser.parse_args()

    main(args.json_path)