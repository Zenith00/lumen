from __future__ import annotations

import flux
from flux import response
import TOKENS
import typing as ty
import functools as fct
import asyncio
import dateparser
from flux.argh import *
import discord
from aiohttp import web
import datetime
# import aiohttp
import webserver
import flux
import aurcore
import contextlib
import logging
import base64

log = logging.Logger("a")
log.setLevel(logging.DEBUG)

if ty.TYPE_CHECKING:
    from flux.context import MessageContext, GuildChannelContext
    from flux.command import *

CHANNEL_PERMS_BOT = discord.PermissionOverwrite(read_messages=True, send_messages=True, add_reactions=True, manage_channels=True, manage_permissions=True)
CHANNEL_PERMS_USER = discord.PermissionOverwrite(read_messages=True, send_messages=True)
CHANNEL_PERMS_FORBIDDEN = discord.PermissionOverwrite(read_messages=False, send_messages=False)


class Roombot:
    def __init__(self):
        self.event_router = aurcore.event.EventRouter(name="roombot")
        self.flux = flux.Flux("roombot", admin_id=TOKENS.ADMIN_ID, parent_router=self.event_router)
        print("init!")

        @self.flux.router.endpoint(":ready")
        def rdy(event: aurcore.event.Event):
            asyncio.get_running_loop().create_task(self.clock())


    async def startup(self, token: str):
        await self.flux.start(token)

    async def shutdown(self):
        await self.flux.logout()

    async def clock(self):
        await self.event_router.submit(aurcore.Event(":tock"))
        await asyncio.sleep(60 * 60)


def str_2_base64(s: str):
    return base64.urlsafe_b64encode(s.encode("ascii")).decode("ascii")


def base64_2_str(s: str):
    return base64.urlsafe_b64decode(s.encode("ascii")).decode("ascii")


async def get_moderator_role(guild: discord.Guild) -> discord.Role:
    return next((role for role in guild.roles if role.permissions.manage_guild), None)


class RoomHandler(flux.FluxCog):
    last_seen_cache: ty.Dict[discord.TextChannel, discord.Message] = {}

    def overwrites_base(self, guild: discord.Guild):
        return {
            guild.default_role: CHANNEL_PERMS_FORBIDDEN,
            guild.me          : CHANNEL_PERMS_BOT
        }

    async def lock_room(self, channel: discord.TextChannel, allow_moderators=False):
        print(f"Locking {channel}")
        overwrites_dict = self.overwrites_base(channel.guild)

        overwrites_dict = {**{target: CHANNEL_PERMS_FORBIDDEN for target in channel.members}, **overwrites_dict}

        if allow_moderators:
            overwrites_dict[get_moderator_role(channel.guild)] = CHANNEL_PERMS_USER

        await asyncio.gather(*[
            channel.set_permissions(target, overwrite=overwrite)
            for target, overwrite in overwrites_dict.items()
        ])

    def route(self):
        @arghify
        @self.flux.commandeer(name="chat", parsed=True)
        async def _(ctx: MessageContext, member: Arg(names=("member",), nargs="+", type=MemberIDType)):
            member_ids = sorted(member)
            members = set([ctx.guild.get_member(member_id) for member_id in member_ids] + [ctx.message.author])
            if len(members) < 2:
                return flux.response.Response(f"Please create a room with at least 2 people!", errored=True)

            overwrites_dict = {
                target: discord.PermissionOverwrite(read_messages=True, send_messages=True) for target in members
            }
            overwrites_dict[ctx.guild.default_role] = discord.PermissionOverwrite(read_messages=False, send_messages=False, manage_channels=False)
            overwrites_dict[ctx.guild.me] = CHANNEL_PERMS_BOT
            text_channel = await ctx.guild.create_text_channel(
                name="-".join([member.name for member in members]),
                # topic=member_encoding,
                category=None,  # todo: add category!
                overwrites=overwrites_dict
            )
            async with ctx.flux.CONFIG.writeable_conf(ctx) as cfg:
                cfg["channels"][text_channel.id] = [member.id for member in members]

            return flux.response.Response(f"Created! {text_channel.mention}")

        @self.flux.commandeer(name="report", parsed=False)
        async def _(ctx: MessageContext):
            """
            report
            Kicks everyone out of the channel and opens it up for moderator inspection
            :param ctx:
            :return:
            """
            await self.lock_room(ctx.channel, allow_moderators=True)
            return flux.response.Response(f"Locking channel! {(await get_moderator_role(ctx.guild)).mention}")

        @self.flux.commandeer(name="leave", parsed=False)
        async def _(ctx: MessageContext, args):
            """
            leave
            Leaves the channel
            :param ctx:
            :param args:
            :return:
            """
            # async def checkmark(ctx: MessageContext, resp: discord.Message):
            #     await resp.add_reaction("\U00002705")
            #     await resp.add_reaction("\U0000274c")
            # print(ctx.channel.id)
            configs = ctx.flux.CONFIG.of(ctx)

            print("leaving!")
            if ctx.channel.id not in configs["channels"]:
                return  flux.response.Response("This can only be used in a roombot channel!", errored=True)
            await ctx.channel.set_permissions(ctx.author, overwrite=None)

            if len(ctx.channel.overwrites) == 1:
                await ctx.channel.delete()
                async with ctx.flux.CONFIG.writeable_conf(ctx) as cfg:
                    del cfg["channels"][ctx.channel.id]
            else:
                async with ctx.flux.CONFIG.writeable_conf(ctx) as cfg:
                    cfg["channels"][ctx.channel.id] = cfg["channels"][ctx.channel.id].remove(ctx.author.id)
                return flux.response.Response(f"{ctx.author.mention} has exited the channel")


        # @self.flux.commandeer(name="close", parsed=False)
        # async def _(ctx: MessageContext, args):
        #     async def checkmark(ctx: MessageContext, resp: discord.Message):
        #         await resp.add_reaction("\U00002705")
        #         await resp.add_reaction("\U0000274c")
        #
        #     yield flux.response.Response(content=f"The channel has been requested to close! \n"
        #                                          f"Please react \U00002705 message to confirm close or \U0000274c to cancel close \n"
        #                                          f"{', '.join([member.mention for member in ctx.channel.members if member != ctx.guild.me])}",
        #                                  post_process=checkmark)
        #
        #     yield flux.response.Response(
        #         content=f"Otherwise, the channel will close automatically after 24 hours of inactivity, currently on:\n"
        #                 f"{(datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime(f'%b %d, UTC %I:%M %p')}"
        #     )
        #
        #     async with ctx.flux.CONFIG.writeable_conf(ctx) as cfg:
        #         closing_channels = cfg.get("closing_channels", {})
        #         closing_channels[str(ctx.channel.id)] = closing_channels.get(str(ctx.channel.id), []) + [ctx.message.author.id]
        #         cfg["closing_channels"] = closing_channels
        #         print(f"closing: {closing_channels}")

        @self.flux.router.endpoint(":message", decompose=True)
        async def update_message_cache(message: discord.Message):
            self.last_seen_cache[message.channel.id] = datetime.datetime.utcnow()


        @self.router.endpoint("roombot:tock")
        async def clean_up_channels(ev: flux.FluxEvent):
            print("Tock!")
            for guild in self.flux.guilds:
                async with self.flux.CONFIG.writeable_conf(guild.id) as cfg:
                    if "closing_channels" not in cfg:
                        return
                    channels_to_check = cfg["closing_channels"]

                closed_channels: ty.Set[discord.TextChannel] = set()
                for channel_id in channels_to_check:
                    channel: discord.TextChannel = self.flux.get_channel(channel_id)
                    if not channel:
                        closed_channels.add(channel)

                    if channel_id in self.last_seen_cache:
                        last_seen = self.last_seen_cache[channel_id].created_at
                    else:
                        last_seen = (await channel.history(limit=1).flatten())[0]

                    if last_seen < (datetime.datetime.utcnow() + datetime.timedelta(days=1)):
                        closed_channels.add(channel.id)
                        await channel.delete(reason=f"24 hours since last activity: {last_seen.isoformat(sep=' ')}")

                async with self.flux.CONFIG.writeable_conf(guild.id) as cfg:
                    cfg["closing_channels"] = list(set(cfg["closing_channels"]) - closed_channels)


roombot = Roombot()
roombot.flux.register_cog(RoomHandler)

aurcore.aiorun(roombot.startup(token=TOKENS.AURTEST), roombot.shutdown())
