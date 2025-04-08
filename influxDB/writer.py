import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import config

class InfluxDBWriter:

    def __init__(self):
        self.token = config.INFLUX.get("token")
        self.org = config.INFLUX.get("org")
        self.url = config.INFLUX.get("url")
        write_client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.bucket = "LiveTele             "
        self.write_api = write_client.write_api(write_options=SYNCHRONOUS)

    def write(self, msg_name, canbus_tag, signals, timestamp):
        for sig, val in signals.items():
            point = (
                    Point(msg_name)
                     .tag("canbus", canbus_tag)
                     .field(sig, float(val))
                     .time(timestamp,write_precision='s')
                     )
            self.write_api.write(bucket=self.bucket, record=point)
