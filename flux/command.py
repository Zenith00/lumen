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


@ext.AutoRepr
class Command:

    def __init__(
            self,
            client: Flux,
            func: ty.Callable[[Context, ...], ty.Awaitable],
            name: str,
            parsing: ParsingType = "basic",

    ):
        self.func = func
        self.client = client
        self.name = name
        self.doc = inspect.getdoc(func)
        self.parsing = parsing
        self.checks: ty.List[ty.Callable[[Context], ty.Awaitable[bool]]] = []
        self.cfg: ty.Dict[str, ty.Any] = {}
        self.argparser: ty.Optional[argparse.ArgumentParser] = None

    async def execute(self, ctx: Context):
        if self.argparser is None:
            raise RuntimeError(f"Command {self} has not been decorated with Argh")

        if ctx.author.id != self.client.admin_id:
            await aio.gather(*[check(ctx) for check in self.checks])

        command_args = ctx.message.content[len(self.cfg["prefix"]) + len(self.name) + 1:].split(" ")
        return await self.func(ctx=ctx, **self.argparser.parse_args(command_args).__dict__)


CommandTransformDeco: ty.TypeAlias = ty.Callable[[Command], Command]


class CommandCheck:
    CheckPredicate: ty.TypeAlias = ty.Callable[[Context], ty.Awaitable[bool]]

    @staticmethod
    def check(*predicates: CheckPredicate) -> CommandTransformDeco:
        def add_checks_deco(command: Command) -> Command:
            command.checks.extend(predicates)
            return command

        return add_checks_deco

    @staticmethod
    def or_(*predicates: CheckPredicate) -> CheckPredicate:
        async def orred_predicate(ctx: Context) -> bool:
            return any(await predicate(ctx) for predicate in predicates)

        return orred_predicate

    @staticmethod
    def and_(*predicates: CheckPredicate) -> CheckPredicate:
        async def anded_predicate(ctx: Context) -> bool:
            return all(await predicate(ctx) for predicate in predicates)

        return anded_predicate

    # @staticmethod
    # def check(func: ty.Callable[[Context], bool]) -> CommandTransformDeco:
    #     def add_check_deco(command: Command) -> Command:
    #         command.checks.append(func)
    #         return command
    # 
    #     return add_check_deco

    @staticmethod
    def whitelist() -> CheckPredicate:
        async def whitelist_predicate(ctx: Context) -> bool:
            if ctx.config is None:
                raise RuntimeError(f"Config has not been initialized for ctx {ctx} in cmd {Command}")
            if not any(identifier in ctx.config["whitelist"] for identifier in ctx.auth_identifiers):
                raise NotWhitelisted()
            return True

        return whitelist_predicate

    @staticmethod
    def has_permissions(
            create_instant_invite=None, kick_members=None, ban_members=None, administrator=None, manage_channels=None, manage_guild=None, add_reactions=None,
            view_audit_log=None, priority_speaker=None, stream=None, read_messages=None, view_channel=None, send_messages=None,
            send_tts_messages=None, manage_messages=None, embed_links=None, attach_files=None, read_message_history=None, mention_everyone=None, external_emojis=None,
            use_external_emojis=None, view_guild_insights=None, connect=None, speak=None, mute_members=None, deafen_members=None,
            move_members=None, use_voice_activation=None, change_nickname=None, manage_nicknames=None, manage_roles=None, manage_permissions=None,
            manage_webhooks=None, manage_emojis=None
    ) -> CheckPredicate:
        perms: ty.Dict[str, bool] = locals()  # keep as first line. avoiding kwargs

        perm_overrides: ty.Dict[str, bool] = {k: perms[k] for k in perms if perms[k] is not None}

        async def perm_predicate(ctx):
            permissions: discord.Permissions = ctx.channel.permissions_for(ctx.author)

            missing = [perm for perm, value in perm_overrides.items() if getattr(permissions, perm) != value]

            if not missing:
                return True

            raise MissingPermissions(missing)

        return perm_predicate

# # noinspection PyShadowingBuiltins
# def add_arg(self,
#             command: Command,
#             *name_or_flags: ty.Text,
#             action: ty.Union[ty.Text, ty.Type[argparse.Action]] = None,
#             nargs: ty.Union[int, ty.Text] = None,
#             const: ty.Any = None,
#             default: ty.Any = None,
#             type_: ty.Union[ty.Callable[[ty.Text], ty.Type], ty.Callable[[str], ty.Type], argparse.FileType] = None,
#             choices: ty.Iterable[ty.Type] = None,
#             required: bool = None,
#             help: ty.Optional[ty.Text] = None,
#             metavar: ty.Optional[ty.Union[ty.Text, ty.Tuple[ty.Text, None]]] = None,
#             dest: ty.Optional[ty.Text] = None,
#             version: ty.Text = None,
#             **kwargs: ty.Any):
#     if command.parsing != "argparse":
#         raise TypeError("Attempted to add argparse arg to non-argparse command")
#     command.argparser.add_argument(name_or_flags=name_or_flags, action=action, nargs=nargs, const=const, default=default, type=type, choices=choices,
#                                    required=required, help=help, metavar=metavar, dest=dest, version=version, **kwargs)
#     return command
