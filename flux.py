import discord
import typing as ty
import functools
import collections as clc
import asyncio
import functools as fct

if ty.TYPE_CHECKING:
    import discord
    from .context import Context
    from .type import *
    from .command import *


class EventMultiplexer:
    def __init__(self, name):
        self.listeners: ty.List[DiscordListener] = []
        self.name = name

    def append_listener(self, listener: ContextFunction):
        self.listeners.append(listener)
        return self

    def generate_coroutine(self):
        async def call(*args, **kwargs):
            print(self.listeners)
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

        @self.register_listener("on_message")
        def command_listener(message: discord.Message):
            context = Context(bot=self, message=message)

    def commandeer(parsing=ParsingType):
        def command_deco(func: ContextFunction):
            return Command(func=func)

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
