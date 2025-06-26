FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV INFLUX_DYNAMICS_URL="https://influx.dynamics-regensburg.de" \
    INFLUX_DYNAMICS_TOKEN="VR3LmlxztFXbxB0z_2IPuLwFxuGMANao1ld8Vsqx8E0NBOUbZBqlmVbiQExawhRuihNQNSbXSvhbXV2Eyc2i0Q==" \
    INFLUX_DYNAMICS_ORG="d1b32e33bc9cbadd" \
    INFLUX_DYNAMICS_BUCKET="LiveTele_Test" \
    INFLUX_REPLAY_URL="https://influx.dynamics-regensburg.de" \
    INFLUX_REPLAY_TOKEN="VR3LmlxztFXbxB0z_2IPuLwFxuGMANao1ld8Vsqx8E0NBOUbZBqlmVbiQExawhRuihNQNSbXSvhbXV2Eyc2i0Q==" \
    INFLUX_REPLAY_ORG="d1b32e33bc9cbadd" \
    INFLUX_REPLAY_BUCKET="LiveTele_Replay" \
    MQTT_HOST="mqtt-livetele.dynamics-regensburg.de" \
    MQTT_PORT="1883" \
    MQTT_USERNAME="liveTele_winApp" \
    MQTT_PASSWORD="dynamics" \
    MQTT_TOPICS="CAN" \
    DBC_1="RP24e_CAN1.dbc" \
    DBC_2="RP24e_CAN2_Inverter.dbc" \
    DBC_3="RP24e_CAN3.dbc"

CMD ["python", "main.py"]