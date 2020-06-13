from __future__ import annotations

import flux
from flux import response
import TOKENS
import typing as ty
import dateparser
from flux.argh import *
from aurcore.event import EventRouter
from aiohttp import web
import aiohttp
import uuid
import TOKENS

if ty.TYPE_CHECKING:
    from flux.context import Context
    from flux.command import *

TODOIST_API = "https://api.todoist.com/sync/v8/sync"
import json

async def handler(request: aiohttp.web.Request):
    # print(f"Recieved reuqest: {request}")
    if request.path == "/webhook/todoist":
        res = await request.json()
        print(res)
        async with aiohttp.ClientSession() as session:
            payload = {
                "token"   : TOKENS.TODOIST,
                "commands": json.dumps([{
                    "type": "item_complete",
                    "uuid": str(uuid.uuid4()),
                    "args": {
                        "id": res["event_data"]["id"]
                    }
                }])
            }
            # payload = {k:json.dumps(v) for k,v in payload.items()}
            print(payload)
            async with session.request('POST', TODOIST_API, params= payload) as req:
                print(req.url)
                print(req)
    return aiohttp.web.Response(text="OK")


class AurServer:
    # @staticmethod

    def __init__(self, parent_router=None):
        self.server = aiohttp.web.Server(handler)
        self.runner = aiohttp.web.ServerRunner(self.server)
        self.event_router = EventRouter(name="discord", parent=parent_router)

    async def start(self):
        await self.runner.setup()
        self.site = aiohttp.web.TCPSite(self.runner, 'localhost', 12000)
        await self.site.start()
