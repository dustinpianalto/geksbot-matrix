import json
from typing import Union
import uuid
import aiohttp
from aiohttp.client_exceptions import ClientConnectionError
import asyncio
from urllib.parse import quote, urlencode, urlparse
from dataclasses import dataclass

MATRIX_API = "/_matrix/client/r0"
MATRIX_MEDIA = "/_matrix/media/r0"


@dataclass
class HTTPConfig:
    max_retry: int = 10
    max_wait_time: int = 3600
    backoff_factor: float = 0.1
    ssl: bool = None
    proxy: str = None


class HTTP:
    def __init__(
        self,
        *,
        base_url: str,
        username: str,
        password: str = None,
        token: str = None,
        device_id: str = None,
        device_name: str = None,
        config: HTTPConfig = HTTPConfig(),
    ):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = token
        self.device_id = device_id
        self.device_name = device_name
        self.access_token = None
        self.config = config
        self.client_session = aiohttp.ClientSession()

    def build_url(
        self, endpoint: str, request_type: str = None, query: dict = None
    ) -> str:
        path = f'{MATRIX_MEDIA if request_type == "MEDIA" else MATRIX_API}/{endpoint}'
        path = self.base_url + quote(path)
        if query:
            path += f"?{urlencode(query)}"
        return path

    def get_wait_time(self, num_timeouts: int) -> float:
        if num_timeouts <= 2:
            return 0.0

        return min(
            self.config.backoff_factor * (2 ** (num_timeouts - 1)),
            self.config.max_wait_time,
        )

    async def close(self):
        if self.client_session:
            await self.client_session.close()
            self.client_session = None

    async def _send(
        self, method: str, path: str, data: dict = None, headers: dict = {}
    ) -> Union[dict, bytes]:
        if not self.client_session:
            self.client_session = aiohttp.ClientSession()

        raw_resp = await self.client_session.request(
            method,
            path,
            json=data,
            ssl=self.config.ssl,
            proxy=self.config.proxy,
            headers=headers,
        )
        if raw_resp.content_type == "application/json":
            return await raw_resp.json()
        else:
            return await raw_resp.read()

    async def send(
        self, method: str, path: str, data: dict = None, content_type: str = None
    ) -> dict:
        if not self.access_token:
            raise RuntimeError("Client is not logged in")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "content_type": content_type or "application/json",
        }

        timeouts = 0

        for _ in range(self.config.max_retry or 1):
            try:
                resp = await self._send(method, path, data, headers)

                if isinstance(resp, bytes):
                    break

                if resp.get("retry_after_ms"):
                    await asyncio.sleep(resp["retry_after_ms"] / 1000)
                else:
                    break
            except (asyncio.TimeoutError, ClientConnectionError, TimeoutError):
                timeouts += 1
                await asyncio.sleep(self.get_wait_time(timeouts))
        else:
            raise RuntimeWarning(f"Max retries reached for {method} - {path} | {data}")

        return resp

    async def login(self):
        path = self.build_url("login")

        data = {}
        if self.password:
            data = {
                "type": "m.login.password",
                "identifier": {"user": self.username, "type": "m.id.user"},
                "password": self.password,
            }
        elif self.token:
            data = {"type": "m.login.token", "token": self.token}
        if self.device_id:
            data["device_id"] = self.device_id
        if self.device_name:
            data["device_name"] = self.device_name

        headers = {"content_type": "application/json"}
        resp = await self._send("post", path, data=data, headers=headers)
        self.access_token = resp.get("access_token")
        self.device_id = resp.get("device_id")
        return resp

    async def logout(self):
        path = self.build_url("logout")
        await self.send("POST", path)
        self.access_token = None

    async def logout_all(self):
        path = self.build_url("logout/all")
        await self.send("POST", path)
        self.access_token = None

    async def room_send(self, room_id: str, event_type: str, content: dict):
        if room_id.startswith("!") and ":" in room_id:
            path = self.build_url(f"rooms/{room_id}/send/{event_type}/{uuid.uuid4()}")
        elif room_id.startswith("#") and ":" in room_id:
            path = self.build_url(f"directory/room/{room_id}")
            resp = await self.send("GET", path)
            if resp.get("room_id"):
                path = self.build_url(
                    f'rooms/{resp["room_id"]}/send/{event_type}/{uuid.uuid4()}'
                )
            else:
                raise RuntimeWarning(resp)
        else:
            raise RuntimeWarning(f"{room_id} is not a valid room id or alias")

        return await self.send("PUT", path, data=content)
