import logging

import paho.mqtt.client as mqtt
import canbus.parser
import config

# def on_connect(client, userdata, flags,reason_code, rc):
#     if rc:
#         print("Error with result code: %d\n", rc)
#     print(f"Connected with result code {reason_code}")
#     client.subscribe("$SYS/#")
#
# def on_message(client, userdata, msg):
#     print(msg.topic + " " + str(msg.payload))
#     canbus.parser(msg)

def create_client(on_connect, on_message):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    logger = logging.getLogger("mqtt")
    logger.setLevel(logging.DEBUG)
    client.enable_logger(logger)
    client.on_connect = on_connect
    client.on_message = on_message
    return client
