from __future__ import annotations

import flux
from flux import response
import TOKENS
import typing as ty
import dateparser
from flux.argh import *
import discord
from aiohttp import web
# import aiohttp
import webserver
import flux
import aurcore
import contextlib
import logging

log = logging.Logger("a")
log.setLevel(logging.DEBUG)

print("Starting aurora!")

if ty.TYPE_CHECKING:
    from flux.context import Context
    from flux.command import *


class Aurora:
    def __init__(self):
        self.event_router = aurcore.event.EventRouter(name="aurora")
        # self.discord = flux.Flux("Aurora", admin_id=TOKENS.ADMIN_ID, parent_router=self.event_router)
        self.discord = discord.Client()
        self.webserver = webserver.AurServer(parent_router=self.event_router)

    async def startup(self, aurora_token: str):
        await self.discord.start(aurora_token)
        # await self.webserver.start()

    async def shutdown(self):
        await self.discord.logout()
        # await self.webserver.runner.shutdown()
        # await self.webserver.runner.cleanup()
        # await self.webserver.server.shutdown()


aurora = Aurora()

# @arghify
# @aurora.discord.commandeer()
# async def remindme(ctx: Context, message: str, duration: Arg(names=("-d",), nargs="*", required=True, action=JoinAction)):
#     print(dateparser.parse(duration))
#     return flux.response.Response()


# @aurora.event_router.endpoint("discord:ready")
# def printy(event: flux.event.Event):
#     print(f"ready! {event}")
#
# #
# @aurora.event_router.endpoint("discord")
# def dbg(event: flux.event.Event):
#     print(f"==dbg: {event}")

# aurora.discord.run(TOKENS.AURORA)
aurcore.aiorun(aurora.startup(aurora_token=TOKENS.AURORA), aurora.shutdown())
