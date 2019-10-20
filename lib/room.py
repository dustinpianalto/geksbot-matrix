# TODO Add Room class
from typing import List, Optional
from datetime import datetime, timedelta

from .client import Client
from .content import MRoomPowerLevelsContent
from .events import StateEvent


class Room:
    def __init__(self, room_id: str, client: Client):
        self.id = room_id
        self.client = client
        self.groups: Optional[List[str]] = None
        self.topic: str = ''
        self.join_rule: Optional[str] = None
        self.version: int = 4
        self.creator: Optional[str] = None
        self.created_at: Optional[datetime] = None
        self.name: Optional[str] = None
        self.aliases: Optional[List[str]] = None
        self.history_visibility: Optional[str] = None
        self.avatar_url: str = ''
        self.canonical_alias: Optional[str] = None
        self.power_levels: Optional[MRoomPowerLevelsContent] = None

    async def update_state(self, state_events: List[StateEvent] = None):
        if not state_events or any([state_event.room.id != self.id for state_event in state_events]):
            path = self.client.api.build_url(f'rooms/{self.id}/state')
            state_events = await self.client.api.send('GET', path)

        for event in state_events:
            if not isinstance(event, StateEvent) or event.type == 'm.room.member':
                continue

            self._update_state(event)

    def _update_state(self, event: StateEvent):
        pass
