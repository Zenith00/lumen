from __future__ import annotations
import flux
from flux import argh
import TOKENS
import typing as ty

if ty.TYPE_CHECKING:
    from flux.context import Context
    from flux.command import *

client = flux.Flux(admin_id=TOKENS.ADMIN_ID)


@argh.argh
@client.commandeer()
async def remindme(ctx: Context, duration):
    print("pong")
#
# @client.commandeer(name="ping")
# async def test(ctx: Context):
#     print("paaaa")

client.run(TOKENS.AURTEST)
