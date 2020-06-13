from __future__ import annotations

import typing as ty
from flux.response import Response
import flux
import discord
import asyncio

if ty.TYPE_CHECKING:
    import datetime


class Interface(flux.FluxCog):
    listening_channels = set()

    def route(self):

        @self.flux.commandeer(name="setup", parsed=False)
        async def setup(ctx: flux.MessageContext, args: str):
            """
            setup
            :param ctx:
            :param args:
            :return:
            """
            configs = self.flux.CONFIG.of(ctx)
            try:
                print("setup!")
                yield Response("Beginning setup... Type `done` to end setup", delete_after=30)

                header_resp = Response("Please select a pair of channels `#from-channel #to-channel`\n"
                                "Once there are `max` pinned messages in #from-channel, the next pin in #from-channel will cause the oldest pin to be converted to an embed and sent in #to-channel\n"
                                f"You can do this in the future without `{ctx.full_command}` via `{configs['prefix']}map #from #to`")
                yield header_resp

                async def check_pair(ev: flux.FluxEvent) -> bool:
                    m: discord.Message = ev.args[0]
                    print(m)
                    if m.author == m.guild.me:
                        return False
                    if m.author != ctx.author:
                        return False
                    if m.content == "cancel":
                        return True
                    if not m.channel_mentions:
                        return False
                    s = flux.utils.find_mentions(m.content)
                    return len(s) == 2

                assignment: discord.Message = (await self.flux.router.wait_for(":message", check_pair, timeout=45)).args[0]

                if assignment.content == "done":
                    yield Response(f"Finished setup {flux.utils.EMOJIS['white_check_mark']}")
                    return

                from_channel, to_channel = flux.utils.find_mentions(assignment.content)
                from_channel, to_channel = self.flux.get_channel(from_channel), self.flux.get_channel(to_channel)
                await assignment.delete()

                resp = Response(f"Mapping pins from {from_channel.mention} to embeds in {to_channel.mention}", delete_after=30)
                yield resp

                async with self.flux.CONFIG.writeable_conf(ctx) as cfg:
                    cfg["pinmap"] = {**cfg.get("pinmap", {}), from_channel.id: to_channel.id}
                await resp.message.add_reaction(flux.utils.EMOJIS["white_check_mark"])

                resp = Response(f"What is the number of native discord pins you would like in {from_channel.mention}? [0-49]\n"
                                f"If you set this to 0, all pins will be immediately turned into embeds\n"
                                f"If you set this to any other number <= 49, {from_channel} will hold that many native discord pins, "
                                f"after which the **oldest** pin will be turned into an embed")

                async def check_max(ev: flux.FluxEvent) -> bool:
                    m: discord.Message = ev.args[0]
                    if m.author == m.guild.me:
                        return False
                    if m.author != m.author:
                        return False
                    return True

                while True:
                    max_resp: discord.Message = (await self.flux.router.wait_for(":message", check_pair, timeout=45)).args[0]
                    try:
                        max_pins = int(max_resp.content)
                        break
                    except ValueError:
                        yield Response("Please enter a number <= 50 and >= 0", delete_after=10)

                async with self.flux.CONFIG.writeable_conf(ctx) as cfg:
                    cfg["maxmap"] = {**cfg.get("maxmap", {}), from_channel.id: max_pins}

                await max_resp.add_reaction(flux.utils.EMOJIS["white_check_mark"])
                if max_pins == 0:
                    yield Response(f"When a message is pinned in {from_channel}, it will be converted into an embed in {to_channel}")
                else:
                    yield Response(f"Once there are {max_pins} pins in {from_channel}, the oldest pin will be converted to an embed in {to_channel}")


            except asyncio.exceptions.TimeoutError:
                yield Response(f"Timed out! Stopping setup process. `{ctx.cfg['prefix']}setup` to restart")
