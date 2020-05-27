from __future__ import annotations
from flux import flux
import TOKENS
import typing as ty

if ty.TYPE_CHECKING:
    from flux.context import Context
    from flux.command import *

client = flux.Flux()


@client.commandeer()
async def ping(ctx: Context):
    print("pong")
#
# @client.commandeer(name="ping")
# async def test(ctx: Context):
#     print("paaaa")

client.run(TOKENS.AURTEST)
