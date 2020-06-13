from __future__ import annotations

import asyncio
import contextlib
import logging
import flux
# import aiohttp
import aurcore
from interface import Interface
from pin_handler import PinHandler
from flux.argh import *
import TOKENS

log = logging.Logger("a")
log.setLevel(logging.DEBUG)

if ty.TYPE_CHECKING:
    from flux.context import MessageContext


class Pinbot:
    def __init__(self):
        self.event_router = aurcore.event.EventRouter(name="roombot")
        self.flux = flux.Flux("pinbot", admin_id=TOKENS.ADMIN_ID, parent_router=self.event_router)
        print("init!")

        @self.flux.router.endpoint(":ready")
        def rdy(event: aurcore.event.Event):
            print("Ready!")

    async def startup(self, token: str):
        await self.flux.start(token)

    async def shutdown(self):
        await self.flux.logout()


pinbot = Pinbot()





pinbot.flux.register_cog(PinHandler)
pinbot.flux.register_cog(Interface)
aurcore.aiorun(pinbot.startup(token=TOKENS.PINBOT), pinbot.shutdown())
