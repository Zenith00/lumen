from __future__ import annotations

import typing as ty

if ty.TYPE_CHECKING:
    import discord
    from .flux import Flux


class Context:
    def __init__(
            self,
            bot: Flux,
            message: discord.Message,
    ):
        self.message = message
        self.bot = bot
        self.config = None

    @property
    def guild(self) -> discord.Guild:
        return self.message.guild

    @property
    def channel(self) -> discord.TextChannel:
        return self.message.channel

    @property
    def author(self) -> discord.User:
        return self.message.author

    @property
    def me(self) -> discord.abc.User:
        return self.guild.me if self.guild else self.bot.user

    @property
    def identifier(self) -> int:
        return self.guild.id or self.author.id

