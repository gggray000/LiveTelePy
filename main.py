from mqtt.client import MqttClient, MqttCredentials
from typing import List
from influxDB.writer import InfluxdbConfig, InfluxDBWriter
from parser.parser import MessageParser
import config

dbcs: List[str] = [config.DBC.get("file1"), config.DBC.get("file2"), config.DBC.get("file3")]
messageParser = MessageParser(dbcs)

influx_config = InfluxdbConfig(
    config.INFLUX.get("token"),
    config.INFLUX.get("org"),
    config.INFLUX.get("url"),
    config.INFLUX.get("bucket")
)

writer = InfluxDBWriter(influx_config)

credentials = MqttCredentials(
    config.MQTT.get("host"),
    config.MQTT.get("port"),
    config.MQTT.get("username"),
    config.MQTT.get("password"),
)

client = MqttClient(credentials, config.MQTT.get("topic"))

# mqtt payload -> list[MqttMessage] -> list[CanMessage] -> List[InfluxMessage] -> IndluxDB points
client.add_callback(
    lambda msg: 
    writer.write(
         messageParser.decode_can_message(
            messageParser.convert_mqtt_to_can(msg)
         )  
    )
)
