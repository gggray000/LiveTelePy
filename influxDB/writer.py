from dataclasses import dataclass
from typing import List
import influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
from messages.types import InfluxMessage


@dataclass
class InfluxdbConfig:

    def __init__(self, token, org, url, bucket):
        self.token = token
        self.org = org
        self.url = url
        self.bucket = bucket

@dataclass
class InfluxDBWriter:

    def __init__(self, config: InfluxdbConfig):
        self.token = config.token
        self.org = config.org
        self.url = config.url
        self.bucket = config.bucket
        write_client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = write_client.write_api(write_options=SYNCHRONOUS)

    def write(self, msgs: List[InfluxMessage]):
        for msg in msgs:
            for sig, val in msg.signals.items():
                point = (
                        Point(msg.name)
                        .field(sig, float(val))
                        .time(msg.timestamp)
                        )
                self.write_api.write(bucket=self.bucket, record=point)
