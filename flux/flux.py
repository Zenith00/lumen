from __future__ import annotations

import asyncio
import functools
import typing as ty

import discord
import traceback
from .command import Command
from .config import Config
from .context import Context
from .errors import *
from .response import Response
from . import utils
from . import argh
import re

if ty.TYPE_CHECKING:
    import discord
    from ._types import *



class EventMultiplexer:
    def __init__(self, name):
        self.listeners: ty.List[DiscordListener] = []
        self.name = name

    def append_listener(self, listener: ContextFunction):
        self.listeners.append(listener)
        return self

    def generate_coroutine(self):
        async def call(*args, **kwargs):
            return await asyncio.gather(*[listener(*args, **kwargs) for listener in self.listeners])

        call.__name__ = self.name
        return call

    @property
    def __name__(self):
        return self.name


class EventDict(dict):
    def __missing__(self, key):
        res = self[key] = EventMultiplexer(name=key)
        return res


def register_builtins(flux: Flux):
    @flux.register_listener("on_message")
    async def command_listener(message: discord.Message):
        if not message.content:
            return
        if message.author is flux.user:
            return

        ctx = Context(bot=flux, message=message)
        flux.CONFIG.attach(ctx)
        print(f"ctx cfg: {ctx}")
        # print(ctx.cfg)
        prefix = ctx.cfg["prefix"]

        if not message.content.startswith(prefix):
            return
        cmd = message.content.split(" ", 1)[0][len(prefix):]
        try:
            res = await flux.commands[cmd].execute(ctx)
        except CommandError as e:
            res = Response(content=str(e), errored=True)
        await res.execute(ctx)

    @argh.arghify
    @flux.commandeer(name="exec", parsed=False)
    async def exec_(ctx: Context, script: str):
        exec_func = utils.sexec
        if any(line.strip().startswith("await") for line in script.split("\n")):
            exec_func = utils.aexec

        with utils.Timer() as t:
            try:
                res = await utils.sexec(script, globals(), locals())
            except Exception as e:
                res = re.sub(r'File ".*[\\/]([^\\/]+.py)"', r'File "\1"', traceback.format_exc(limit=1))
        return Response((f""
                         f"Ran in {t.elapsed * 1000:.2f} ms\n"
                         f"**IN**:\n"
                         f"```py\n{script}\n```"
                         f"**OUT**:\n"
                         f"```py\n{res}\n```"))


class Flux(discord.Client):
    CONFIG = Config()

    def __init__(self, admin_id: int, *args, **kwargs):
        super(Flux, self).__init__(*args, **kwargs)
        self.listeners = EventDict()
        self.commands: ty.Dict[str, Command] = {}
        self.admin_id = admin_id
        register_builtins(self)

    def commandeer(self, name: ty.Optional[str] = None, parsed: bool = True) -> ty.Callable[[ty.Callable[[...], ty.Awaitable[Response]]], Command]:
        def command_deco(func: ty.Callable[[...], ty.Awaitable[Response]]) -> Command:
            cmd = Command(client=self, func=func, name=(name or func.__name__), parsed=parsed)

            if cmd.name in self.commands:
                raise TypeError(f"Attempting to register command {cmd} when {self.commands[cmd.name]} already exists")
            self.commands[cmd.name] = cmd
            return cmd

        return command_deco

    def register_listener(self, listen_for: str, discord=True) -> ty.Callable[[DiscordListener], None]:
        def deco(listener: DiscordListener):
            @functools.wraps(listener)
            async def compat_layer(*args, **kwargs):
                # preprocessing
                await listener(*args, **kwargs)
                # postprocessing

            self.listeners[listen_for].append_listener(compat_layer)
            if discord:
                self.event(self.listeners[listen_for].generate_coroutine())

        return deco


class FluxCommand:
    pass
