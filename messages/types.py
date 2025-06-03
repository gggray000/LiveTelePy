from typing import List, Dict, Union
from dataclasses import dataclass, field

@dataclass
class MqttMessage:
    timestamp: float = field(default=0)
    state: int = field(default=0)
    dup: bool = field(default=False)
    mid: int = field(default=-1)
    topic: str = field(default="")
    payload: bytes = field(default=b"")
    qos: int = field(default=0)
    retain: bool = field(default=False)

    def __str__(self) -> str:
        return f"{self.payload=}"

    def copy(self):
        msg = MqttMessage()
        msg.timestamp = self.timestamp
        msg.state = self.state
        msg.dup = self.dup
        msg.mid = self.mid
        msg.topic = self.topic
        msg.payload = self.payload
        msg.qos = self.qos
        msg.retain = self.retain
        return msg

@dataclass
class CanMessage:
    timestamp: float = field(default=0)
    msg_id: int = field(default=0)
    dlc: int = field(default=0)
    # Different that livetele_applications, because here we decode using DBC files.
    data: bytes = field(default=b"")
    can_bus: int = field(default=0)

    def __str__(self) -> str:
        return f"{self.timestamp=}\n{self.msg_id}\n{self.msg_id=}\n{self.dlc=}\n{self.data=}"

@dataclass
class InfluxMessage:
    name: str = field(default="")
    signals: Dict[str, Union[int, float]] = field(default_factory=dict)
    timestamp: float = field(default=0)

    def __str__(self) -> str:
        return f"Message:{self.name=}\nSignals{self.signals}\n"
