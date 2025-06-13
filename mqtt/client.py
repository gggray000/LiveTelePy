import socket
from typing import List, Callable
from messages.types import MqttMessage
import paho.mqtt.client as mqtt
import config


class MqttCredentials:

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

class MqttClient:

    def __init__(self, credentials: MqttCredentials, topics: List[str]):
        self.client = mqtt.Client()
        self.client.username_pw_set(credentials.username, credentials.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.callbacks = []
        self.topics = topics

    def add_callback(self, func: Callable):
        self.callbacks.append(func)

    def add_topic(self, topic: str) -> None:
        self.topics.append(topic)

    def subscribe_all_topics(self) -> None:
        for topic in self.topics:
            self.client.subscribe(topic)

    def connect(self) -> bool:
        try:
            self.client.connect(config.MQTT.get("host"), config.MQTT.get("port"))
            self.client.loop_forever()
            return True
        except socket.gaierror as e:
            print(f"IP could not be resolved: {config.MQTT.get("host")}")
            print(f"Check that you have internet access and spelled the ip correctly")
            print(e)
            return False
        except TimeoutError:
            print(f"Client connect failed! Check for correct internet access, ip, port, credentials, ...")
            print(f"Set values: {config.MQTT.get("host")=}")
            return False

    def stop(self) -> None:
        self.client.loop_stop()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT server.")
            self.subscribe_all_topics()
        else:
            print("Connection failed")

    def on_message(self, message: mqtt.MQTTMessage) -> None:

        msg = MqttMessage()
        msg.timestamp = message.timestamp
        msg.state = message.state
        msg.dup = message.dup
        msg.mid = message.mid
        msg.topic = message.topic
        msg.payload = message.payload
        msg.qos = message.qos
        msg.retain = message.retain

        for func in self.callbacks:
            func(msg)



