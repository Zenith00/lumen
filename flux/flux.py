from __future__ import annotations

import asyncio
import functools
import typing as ty

import discord

from .command import Command
from .config import Config
from .context import Context

if ty.TYPE_CHECKING:
    import discord
    from ._types import *

CONFIG = Config()


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


class Flux(discord.Client):

    def __init__(self, *args, **kwargs):
        super(Flux, self).__init__(*args, **kwargs)
        self.listeners = EventDict()
        self.commands: ty.Dict[str, Command] = {}

        @self.register_listener("on_message")
        async def command_listener(message: discord.Message):
            if not message.content:
                return
            ctx = Context(bot=self, message=message)
            with CONFIG.of(ctx) as cfg:
                prefix = cfg["prefix"]
                ctx.config = cfg

                if message.content.startswith(prefix):
                    cmd = message.content.split(" ", 1)[0][len(prefix):]
                    await self.commands[cmd].execute(ctx)

    def commandeer(self, name: ty.Optional[str] = None, parsing: ParsingType = "basic"):
        def command_deco(func: ContextFunction):
            cmd = Command(func=func, parsing=parsing)
            cmd_name = name or func.__name__
            if cmd_name in self.commands:
                raise TypeError(f"Attempting to register command {cmd} as {cmd_name} when {self.commands[cmd_name]} already exists")
            self.commands[name or func.__name__] = cmd

        return command_deco

    def register_listener(self, listen_for: str):
        def deco(listener: DiscordListener):
            @functools.wraps(listener)
            async def compat_layer(*args, **kwargs):
                # preprocessing
                await listener(*args, **kwargs)
                # postprocessing

            self.listeners[listen_for].append_listener(compat_layer)
            self.event(self.listeners[listen_for].generate_coroutine())

        return deco


class FluxCommand:
    pass
