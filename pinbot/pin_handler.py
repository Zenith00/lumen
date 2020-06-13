from __future__ import annotations

import typing as ty
import flux

if ty.TYPE_CHECKING:
    import discord
    import datetime


class PinHandler(flux.FluxCog):
    listening_channels = set()

    def route(self):
        @self.router.endpoint("flux:guild_channel_pins_update", decompose=True)
        async def message_update_handler(channel: discord.TextChannel, last_pin: datetime.datetime):
            if channel.id not in self.listening_channels:
                return
            pins = await channel.pins()

