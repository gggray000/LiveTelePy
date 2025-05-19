import json
import base64
from pathlib import Path
from canbus.dbc_loader import load_dbc
from influxDB.writer import InfluxDBWriter
from cantools.database.errors import DecodeError
import config

# Load DBCs
dbc1 = load_dbc(config.DBC.get("file1"))
dbc3 = load_dbc(config.DBC.get("file3"))

writer = InfluxDBWriter(config.INFLUX_REPLAY)

def process_payload(payload_bytes):
    for offset in range(0, len(payload_bytes) - 17 + 1, 17):
        arbitration = ((payload_bytes[offset] << 8) | payload_bytes[offset + 1]) & 0x7FF
        can_bus = payload_bytes[offset + 4] >> 4
        dlc = payload_bytes[offset + 4] & 0x0F
        can_data = payload_bytes[offset + 5: offset + 5 + dlc]
        timestamp = (
            (payload_bytes[offset + 13] << 24) |
            (payload_bytes[offset + 14] << 16) |
            (payload_bytes[offset + 15] << 8) |
            payload_bytes[offset + 16]
        )

        print(f"\n[CAN BUS {can_bus}] ID: {arbitration}, DLC: {dlc}, Timestamp: {timestamp}")
        print("Data:", " ".join(f"{byte:02x}" for byte in can_data))

        if can_bus not in (0, 1):
            print(f"Unknown CAN bus {can_bus}, skipping.")
            continue

        dbc = dbc1 if can_bus == 0 else dbc3
        msg_def = dbc._frame_id_to_message.get(arbitration)
        if not msg_def:
            print(f"No message definition for ID {arbitration}, skipping.")
            continue

        if len(can_data) < msg_def.length:
            print(f"Truncated data for ID {arbitration}, skipping.")
            continue

        try:
            signals = msg_def.decode(can_data, allow_truncated=True)
            print(f"Message: {msg_def.name} => Signals: {signals}")
            writer.write(msg_def.name, f"canbus{can_bus}", signals, timestamp)
        except DecodeError as e:
            print(f"DecodeError for ID {arbitration}: {e}")

def main(json_path):
    with open(json_path, 'r') as f:
        clients = json.load(f)

    for client in clients:
        messages = client.get("messages", [])
        for msg in messages:
            # Try the most likely place first
            payload_base64 = msg.get("payload") or msg.get("properties", {}).get("payload")
            if not payload_base64:
                print("No payload found in message, skipping.")
                continue

            try:
                payload_bytes = base64.b64decode(payload_base64)
                process_payload(payload_bytes)
            except Exception as e:
                print(f"Failed to process payload: {e}")

if __name__ == "__main__":
    # import sys
    # if len(sys.argv) != 2:
    #     print("Usage: python replay_from_json.py <path_to_json_file>")
    #     exit(1)
    #
    # main(Path(sys.argv[1]))
    main("/Users/ganruilin/Desktop/LiveTele/test_17_05.json")