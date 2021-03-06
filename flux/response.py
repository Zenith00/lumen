from __future__ import annotations
from . import ext

import typing as ty

if ty.TYPE_CHECKING:
    import discord
    from .context import MessageContext
    from ._types import *
    from .errors import *
    from .flux import Flux

import typing as ty
import itertools as itt
import asyncio as aio
import inspect
import flux
import argparse
import datetime


class Response:
    __iter_done = False
    message: ty.Optional[discord.Message]

    def __init__(
            self,
            # ctx: Context,
            content: ty.Optional[str] = None,
            embed: ty.Optional[discord.Embed] = None,
            delete_after: ty.Optional[ty.Union[float, datetime.timedelta]] = None,
            reaction: ty.Optional[ty.Iterable[ty.Union[discord.Emoji, str]]] = None,
            errored: bool = False,
            ping: bool = False,
            post_process: ty.Optional[ty.Callable[[MessageContext, discord.Message], ty.Coroutine]] = None,
            trashable: bool = False
            # reaction: str = ""  # todo: white check mark
    ):
        self.content = content
        self.embed = embed
        self.delete_after = delete_after if isinstance(delete_after, datetime.timedelta) or not delete_after else datetime.timedelta(seconds=delete_after)
        self.errored = errored
        self.reactions = reaction or (("❌",) if self.errored else ("✅",))
        self.ping = ping
        self.post_process = post_process or (lambda *_: aio.sleep(0))
        self.trashable = trashable

    async def execute(self, ctx: MessageContext):

        if self.content or self.embed:
            message = await ctx.channel.send(
                content=self.content if self.content else "" + (ctx.author.mention if self.ping else ""),
                embed=self.embed,
                delete_after=self.delete_after.seconds if self.delete_after else None  # todo: check if seconds,

            )
            self.message = message

            await self.post_process(ctx, message)

        for reaction in self.reactions:
            await ctx.message.add_reaction(reaction)
        if self.trashable:
            await ctx.message.add_reaction(flux.utils.EMOJIS["trashcan"])
            try:
                await ctx.flux.router.wait_for("reaction_add", check=lambda ev: ev.args[0].id == self.message.id and ev.args[1] == ctx.message.author, timeout=15)
                await self.message.delete()
            except aio.exceptions.TimeoutError:
                await ctx.message.remove_reaction(emoji=flux.utils.EMOJIS["trashcan"], member=ctx.guild.me)

    # def __aiter__(self):
    #     async def gen():
    #         yield self
    #     return gen()
