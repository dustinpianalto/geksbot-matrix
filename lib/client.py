import asyncio
from typing import Union, Optional

from .api import API, APIConfig


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
        self.rooms: list = []
        self.api: Optional[API] = None
        self.running: bool = False
        self.sync_timeout: int = 1000
        self.sync_since: Optional[str] = None
        self.sync_full_state: bool = False
        self.sync_set_presence: str = "online"
        self.sync_filter: Optional[str] = None
        self.sync_delay: Optional[str] = None

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
                self.process_events(key, value)

    def process_events(self, event_type: str, event: dict):
        if event_type == "rooms":
            joined_room_events = event["join"]
            invited_rooms = event["invite"]
            left_rooms = event["leave"]
        # TODO process events

    def process_timeline(self, room, timeline):
        # TODO process the timeline
        pass
