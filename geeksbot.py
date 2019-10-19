import json
import asyncio
from nio import (AsyncClient, RoomMessageText)
import logging

log_format = '%(asctime)s ||| %(name)s | %(levelname)s | %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)
logger = logging.getLogger('geeksbot')
logger.setLevel(logging.INFO)


class Geeksbot(AsyncClient):
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        super(Geeksbot, self).__init__(self.base_url, self.username)
        self.add_event_callback(self.on_message, RoomMessageText)

    async def login(self):
        await super(Geeksbot, self).login(self.password)

    async def on_message(self, room, event):
        logger.info(f'Message recieved for room {room.display_name} | {room.user_name(event.sender)}: {event.body}')
        if event.body.startswith('$say '):
            msg = {
                "body": event.body.split(' ', 1)[1],
                "msgtype": 'm.text'
            }
            print(msg)
            resp = await self.room_send(room.room_id, 'm.room.message', msg)
            print(resp)


async def main():
    with open('config.json') as f:
        config = json.load(f)
    client = Geeksbot(**config)

    await client.login()
    await client.sync_forever(timeout=1000)

asyncio.get_event_loop().run_until_complete(main())