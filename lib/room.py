# TODO Add Room class
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from .content import (
    MRoomPowerLevelsContent,
    MRoomAliasesContent,
    MRoomBotOptionsContent,
    MRoomCanonicalAliasContent,
    MRoomCreateContent,
    MRoomHistoryVisibilityContent,
    MRoomJoinRulesContent,
    MRoomNameContent,
    MRoomRelatedGroupsContent,
    MRoomTopicContent
)
from .utils import PreviousRoom


class Room:
    def __init__(self, room_id: str, client):
        from .client import Client
        self.id = room_id
        self.client: Client = client
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
        self.bot_options: Optional[Dict[str, dict]] = None
        self.federated: bool = True
        self.predecessor: Optional[PreviousRoom] = None
        self.heroes: Optional[List[str]] = None
        self.joined_member_count: Optional[int] = None
        self.invited_member_count: Optional[int] = None

    async def update_state(self, state_events: list = None):
        from .events import StateEvent

        if not state_events or any([state_event.room_id != self.id for state_event in state_events]):
            path = self.client.api.build_url(f'rooms/{self.id}/state')
            state_events = await self.client.api.send('GET', path)

        for event in state_events:
            if not isinstance(event, StateEvent) or event.type == 'm.room.member':
                continue

            self._update_state(event)

    def _update_state(self, event):
        content = event.content
        if isinstance(content, MRoomTopicContent):
            self.topic = content.topic
        elif isinstance(content, MRoomNameContent):
            self.name = content.name
        elif isinstance(content, MRoomRelatedGroupsContent):
            self.groups = content.groups
        elif isinstance(content, MRoomJoinRulesContent):
            self.join_rule = content.join_rule
        elif isinstance(content, MRoomHistoryVisibilityContent):
            self.history_visibility = content.history_visibility
        elif isinstance(content, MRoomCreateContent):
            self.creator = content.creator
            self.federated = content.m_federate
            self.version = content.room_version
            self.predecessor = content.predecessor
        elif isinstance(content, MRoomCanonicalAliasContent):
            self.canonical_alias = content.alias
        elif isinstance(content, MRoomAliasesContent):
            self.aliases = content.aliases
        elif isinstance(content, MRoomBotOptionsContent):
            self.bot_options = content.options
        elif isinstance(content, MRoomPowerLevelsContent):
            self.power_levels = content
