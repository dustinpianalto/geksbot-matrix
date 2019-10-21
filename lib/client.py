import asyncio
from typing import Union, Optional, Dict

from .api import API, APIConfig
from .room import Room


class Client:
    def __init__(
        self,
        prefix: Union[str, list, tuple],
        homeserver: str = "https://matrixcoding.chat",
    ):
        self.prefix = prefix
        self.homeserver = homeserver
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.token: Optional[str] = None
        self.rooms: Dict[str, Room] = {}
        self.api: Optional[API] = None
        self.running: bool = False
        self.sync_timeout: int = 1000
        self.sync_since: Optional[str] = None
        self.sync_full_state: bool = False
        self.sync_set_presence: str = "online"
        self.sync_filter: Optional[str] = None
        self.sync_delay: Optional[str] = None
        self.sync_process_dispatcher = {
            'presence': self.process_presence_events,
            'rooms': self.process_room_events,
            'groups': self.process_group_events
        }

    async def run(self, user_id: str = None, password: str = None, token: str = None):
        if not password and not token:
            raise RuntimeError("Either the password or a token is required")
        self.api = API(
            base_url=self.homeserver, user_id=user_id, password=password, token=token
        )
        resp = await self.api.login()
        if resp.get("errcode"):
            raise RuntimeError(resp)
        self.running = True
        while self.running:
            if self.sync_delay:
                await asyncio.sleep(self.sync_delay)
            await self.sync()

    async def sync(self):
        resp = await self.api.get_sync(
            self.sync_filter,
            self.sync_since,
            self.sync_full_state,
            self.sync_set_presence,
            self.sync_timeout,
        )
        if resp.get("errcode"):
            self.running = False
            raise RuntimeError(resp)
        self.sync_since = resp["next_batch"]
        for key, value in resp.iteritems():
            if key == "next_batch":
                self.sync_since = value
            else:
                if key in self.sync_process_dispatcher:
                    self.sync_process_dispatcher[key](value)

    def process_presence_events(self, value: dict):
        events = value['events']
        for event_dict in events:
            event = self.process_event(event_dict)
            # TODO Do something with presence event...

    def process_room_events(self, value: dict):
        self.process_room_join_events(value['join'])
        self.process_room_invite_events(value['invite'])
        self.process_room_leave_events(value['leave'])

    def process_room_join_events(self, rooms: dict):
        for room_id, data in rooms.iteritems():
            if room_id not in self.rooms:
                self.rooms[room_id] = Room(room_id, self)
            room = self.rooms[room_id]

            # Process state events and update Room state
            state_events = []
            for event_dict in data['state']['events']:
                event_dict['room'] = room
                state_events.append(self.process_event(event_dict))
            room.update_state(state_events)

            # Process timeline
            timeline_events = []
            for event_dict in data['timeline']['events']:
                event_dict['room'] = room
                timeline_events.append(self.process_event(event_dict))

    def process_room_invite_events(self, rooms: dict):
        pass

    def process_room_leave_events(self, rooms: dict):
        pass

    def process_group_events(self, value: dict):
        pass

    def process_event(self, event: dict):
        from .events import EventBase, RoomEvent, StateEvent, RedactionEvent, MessageEvent
        if event.get('redacted'):
            return RedactionEvent.from_dict(self, event)
        elif event.get('state_key'):
            return StateEvent.from_dict(self, event)
        elif event['type'] == 'm.presence':
            return EventBase.from_dict(self, event)
        elif event['type'] == 'm.room.message':
            return MessageEvent.from_dict(self, event)
        else:
            return RoomEvent.from_dict(self, event)

    def process_timeline(self, room, timeline):
        # TODO process the timeline
        pass
