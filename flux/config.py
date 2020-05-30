from __future__ import annotations

import typing as ty
from . import ext

if ty.TYPE_CHECKING:
    from .context import Context
    from .command import Command
    from ._types import *
import yaml
import functools as fct
import pathlib as pl
import collections as clc
import contextlib
import asyncio.locks

CONFIG_DIR = pl.Path("./.lumenconf/")
CONFIG_DIR.mkdir(exist_ok=True)

CACHED_CONFIGS = 100


@ext.AutoRepr
class Config:

    def __init__(self):
        self.config_dir = CONFIG_DIR
        with (CONFIG_DIR / "base.yaml").open("r") as f:
            self.base_config = yaml.safe_load(f)
        self.cached: clc.OrderedDict = clc.OrderedDict()  # mypy weirdness
        self.locks: ty.Dict[int, asyncio.locks.Lock] = clc.defaultdict(asyncio.locks.Lock)

    def write_config(self, config_identifier, data):
        local_config_path: pl.Path = self.config_dir / f"{config_identifier}.yaml"
        with local_config_path.open("w") as f:
            yaml.safe_dump(data, f)

    def load_config(self, config_identifier):
        local_config_path: pl.Path = CONFIG_DIR / f"{config_identifier}.yaml"
        try:
            with local_config_path.open("r") as f:
                local_config = yaml.safe_load(f)
        except FileNotFoundError:
            local_config = {}
        return local_config

    def attach(self, ctx: Context) -> ty.Dict[str, ty.Any]:
        if ctx.config_identifier in self.cached:
            self.cached.move_to_end(ctx.config_identifier, last=False)
            configs = self.cached[ctx.config_identifier]
        else:
            print(f"Loading config context {ctx} {ctx.config_identifier}")

            local_config = self.load_config(ctx.config_identifier)
            combined_dict = {**self.base_config, **local_config}
            cleaned_dict = {k: combined_dict[k] for k in self.base_config}

            if cleaned_dict != local_config:
                self.write_config(ctx.config_identifier, cleaned_dict)

            self.cached[ctx.config_identifier] = cleaned_dict
            if len(self.cached) > CACHED_CONFIGS:
                self.cached.popitem()

            configs = cleaned_dict

        ctx.cfg = configs
        return configs
        # try:
        #     yield combined_dict
        # finally:
        #     with local_config_path.open("w") as f:
        #         yaml.safe_dump(cleaned_dict, f)

    #
    # def lock_conf(self, func: ContextFunction):
    #     @fct.wraps(func)
    #     async def lock_wrapper(ctx: Context, *args, **kwargs):
    #         async with self.locks[ctx.config_identifier]:
    #             res = await func(ctx, *args, **kwargs)
    #         del self.locks[ctx.config_identifier]
    #         return res
    #
    #     return lock_wrapper

    @contextlib.asynccontextmanager
    async def writeable_conf(self, ctx):
        async with self.locks[ctx.config_identifier]:
            try:
                output_dict = self.attach(ctx)
                yield output_dict
            finally:
                self.write(ctx.config_identifier, output_dict)
        del self.locks[ctx.config_identifier]
