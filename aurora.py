from __future__ import annotations

import flux
from flux import response
import TOKENS
import typing as ty
import dateparser
from flux.argh import *

if ty.TYPE_CHECKING:
    from flux.context import Context
    from flux.command import *

client = flux.Flux(admin_id=TOKENS.ADMIN_ID)


@arghify
@client.commandeer()
async def remindme(ctx: Context, message: str, duration: Arg(names=("-d",), nargs="*", required=True, action=JoinAction)):
    print(message)
    print(duration)
    print(dateparser.parse(duration))
    print("pong")
    return flux.response.Response()


#
# @client.commandeer(name="ping")
# async def test(ctx: Context):
#     print("paaaa")

client.run(TOKENS.AURTEST)
