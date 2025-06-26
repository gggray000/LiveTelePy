import os

INFLUX_REPLAY = {
    "url": os.getenv("INFLUX_REPLAY_URL"),
    "token": os.getenv("INFLUX_REPLAY_TOKEN"),
    "org": os.getenv("INFLUX_REPLAY_ORG"),
    "bucket": os.getenv("INFLUX_REPLAY_BUCKET"),
}

INFLUX_DYNAMICS = {
    "url": os.getenv("INFLUX_DYNAMICS_URL"),
    "token": os.getenv("INFLUX_DYNAMICS_TOKEN"),
    "org": os.getenv("INFLUX_DYNAMICS_ORG"),
    "bucket": os.getenv("INFLUX_DYNAMICS_BUCKET"),
}

MQTT = {
    "host": os.getenv("MQTT_HOST"),
    "port": os.getenv("MQTT_PORT"),
    "username": os.getenv("MQTT_USERNAME"),
    "password": os.getenv("MQTT_PASSWORD"),
    "topics": os.getenv("MQTT_TOPICS").split(","),
}

DBC = {
    "file1":os.getenv("DBC_1"),
    "file2":os.getenv("DBC_2"),
    "file3":os.getenv("DBC_3"),
}