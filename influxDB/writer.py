import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import config

class InfluxDBWriter():

    def __init__(self, config_name):
        self.token = config_name.get("token")
        self.org = config_name.get("org")
        self.url = config_name.get("url")
        write_client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.bucket = config_name.get("bucket")
        self.write_api = write_client.write_api(write_options=SYNCHRONOUS)

    def write(self, msg_name, canbus_tag, signals, timestamp):
        for sig, val in signals.items():
            point = (
                    Point(msg_name)
                     .tag("canbus", canbus_tag)
                     .field(sig, float(val))
                     .time(None)
                     )
            self.write_api.write(bucket=self.bucket, record=point)
