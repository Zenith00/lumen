from __future__ import annotations

import typing as ty
from . import ext

if ty.TYPE_CHECKING:
    import discord
    from .flux import Flux


@ext.AutoRepr
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
    def author(self) -> ty.Union[discord.User, discord.Member]:
        return self.message.author

    @property
    def me(self) -> discord.abc.User:
        return self.guild.me if self.guild else self.bot.user

    @property
    def config_identifier(self) -> int:
        return self.guild.id or self.author.id

    @property
    def auth_identifiers(self) -> ty.List[int]:
        identifiers = [self.author.id]
        if self.guild:
            identifiers.extend([role.id for role in self.author.roles])
        return identifiers

