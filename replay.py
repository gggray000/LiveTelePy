import argparse
import base64
import datetime
import json
import matplotlib.pyplot as plt
from typing import List

import pytz
from influxDB.writer import InfluxdbConfig, InfluxDBWriter
from messages.types import MqttMessage, CanMessage
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

def plot(all_can_msgs: List[List[CanMessage]]):
            
                all_timestamps = []
            
                for can_msgs in all_can_msgs:
                     average_timestamp_s= sum((msg.timestamp / 1e9) for msg in can_msgs) / len(can_msgs)
                     all_timestamps.append(average_timestamp_s)

                plt.figure(figsize=(12, 6))
                plt.scatter(all_timestamps, range(len(all_timestamps)), marker='o', label='Avg Timestamp per MQTT Payload')
                plt.title("Average Timestamps of MQTT Payloads")
                plt.xlabel("Timestamp (UTC)")
                plt.ylabel("Payload Index")
                plt.grid(True)
                plt.legend()
                plt.tight_layout()
                plt.xticks(rotation=45)
                plt.show()

def main(json_path, mqtt_msg=None):
    all_can_msgs = []

    with open(json_path, 'r') as f:
        clients = json.load(f)
    try: 
        for client in clients:
            messages = client.get("messages", [])
            for msg in messages:
                payload_base64 = msg.get("payload") or msg.get("properties", {}).get("payload")
                if not payload_base64:
                    print("No payload found in messages, skipping.")
                    continue
                try:
                     
                    #print("\nRaw payload: " + payload_base64)
                    payload_bytes = base64.b64decode(payload_base64)
                    #print("\nPayload after base64 decoding: ")
                    #print(payload_bytes)
                    #print(f"\nPayload contains messages: {len(payload_bytes)/17}")

                    mock_mqtt_msg = MqttMessage(
                        payload=payload_bytes,
                        topic=msg.get("topic", ""),
                        timestamp=msg.get("timestamp", 0)
                    )


                    can_msgs = messageParser.convert_mqtt_to_can(mock_mqtt_msg)
                    all_can_msgs.append(can_msgs)

                

                    #influx_msgs = messageParser.decode_can_message(can_msgs)
                    #writer.write(influx_msgs)

                    #for influx_msg in influx_msgs:
                        #print(influx_msg)

                except Exception as e:
                    print(f"Failed to process payload: {e}")

    except KeyboardInterrupt:
        print("\nShutdown signal received. Plotting average timestamps...")
        plot(all_can_msgs)
    
    return all_can_msgs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write logged MQTT messages to InfluxDB from a JSON file")
    parser.add_argument("json_path", help="Path to the JSON file")
    args = parser.parse_args()

    plot(main(args.json_path))