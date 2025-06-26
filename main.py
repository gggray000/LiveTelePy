from mqtt.client import MqttClient, MqttCredentials
from typing import List
from influxDB.writer import InfluxdbConfig, InfluxDBWriter
from parser.parser import MessageParser
import config
import urllib3
from dotenv import load_dotenv

load_dotenv()

# TODO: Resolve SSL issue
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

dbcs: List[str] = [config.DBC.get("file1"), config.DBC.get("file2"), config.DBC.get("file3")]
messageParser = MessageParser(dbcs)

influx_config = InfluxdbConfig(
    config.INFLUX_DYNAMICS.get("token"),
    config.INFLUX_DYNAMICS.get("org"),
    config.INFLUX_DYNAMICS.get("url"),
    config.INFLUX_DYNAMICS.get("bucket")
)

writer = InfluxDBWriter(influx_config)

credentials = MqttCredentials(
    config.MQTT.get("host"),
    config.MQTT.get("port"),
    config.MQTT.get("username"),
    config.MQTT.get("password"),
)

client = MqttClient(credentials, config.MQTT.get("topics"))

# mqtt payload -> list[MqttMessage] -> list[CanMessage] -> List[InfluxMessage] -> InfluxDB points
client.add_callback(
    lambda msg: 
    writer.write(
         messageParser.decode_can_message(
            messageParser.convert_mqtt_to_can(msg)
         )  
    )
)

client.connect()