from __future__ import annotations

import typing as ty

if ty.TYPE_CHECKING:
    from .context import Context

import yaml
import pathlib as pl
import collections as clc
import contextlib

CONFIG_DIR = pl.Path("./.lumenconf/")
CONFIG_DIR.mkdir(exist_ok=True)


class Config:
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.base_config = (CONFIG_DIR + "/base.yaml").read_text()
        self.cached: clc.OrderedDict = clc.OrderedDict()  # mypy weirdness

    @contextlib.contextmanager
    def of(self, ctx: Context):
        local_config_path: pl.Path = CONFIG_DIR / f"{ctx.identifier}.yaml"
        with local_config_path.open("r") as f:
            local_config = yaml.load(f)

        merged_dict = {k: local_config[k] or self.base_config[k] for k in self.base_config}

        try:
            yield merged_dict
        finally:
            with local_config_path.open("w") as f:
                yaml.dump(merged_dict, f)
