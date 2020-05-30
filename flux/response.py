from __future__ import annotations
from . import ext

import typing as ty

if ty.TYPE_CHECKING:
    import discord
    from .context import Context
    from ._types import *
    from .errors import *
    from .flux import Flux

import typing as ty
import itertools as itt
import asyncio as aio
import inspect
import argparse
import datetime


class Response:
    def __init__(
            self,
            # ctx: Context,
            content: ty.Optional[str] = None,
            embed: ty.Optional[discord.Embed] = None,
            delete_after: ty.Optional[datetime.timedelta] = None,
            reaction: ty.Optional[ty.Union[discord.Emoji, str]] = "✅",
            errored: bool = False,
            ping: bool = False,
            # reaction: str = ""  # todo: white check mark
    ):
        self.content = content
        self.embed = embed
        self.delete_after = delete_after
        self.reaction = reaction
        self.ping = ping

    async def execute(self, ctx: Context):
        if self.content or self.embed:
            await ctx.channel.send(
                content=self.content + (ctx.author.mention if self.ping else ""),
                embed=self.embed,
                delete_after=self.delete_after.seconds if self.delete_after else None  # todo: check if seconds
            )
        if self.reaction:
            await ctx.message.add_reaction(self.reaction)
