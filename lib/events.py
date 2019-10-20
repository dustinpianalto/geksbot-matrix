from dataclasses import dataclass
from typing import Optional, List

from .room import Room
from .content import ContentBase


@dataclass
class EventBase:
    content: ContentBase
    type: str
    sender: str


@dataclass
class UnsignedData:
    age: int
    redacted_because: Optional[EventBase] = None
    transaction_id: Optional[str] = None
    invite_room_state: Optional[List[EventBase]] = None


@dataclass
class RoomEvent(EventBase):
    event_id: str
    origin_server_id: int
    unsigned: UnsignedData
    room: Room


@dataclass
class StateEvent(RoomEvent):
    state_key: str
    prev_content: Optional[EventBase] = None


@dataclass
class RedactionEvent(RoomEvent):
    redacts: EventBase
