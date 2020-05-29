from __future__ import annotations

from flux.argh import *

@argh
def test(a, b: int =1, c: Arg() = None):
    pass


test(1,2,3)