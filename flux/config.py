from __future__ import annotations

import typing as ty
from . import ext

if ty.TYPE_CHECKING:
    from .context import Context

import yaml
import pathlib as pl
import collections as clc
import contextlib

CONFIG_DIR = pl.Path("./.lumenconf/")
CONFIG_DIR.mkdir(exist_ok=True)


@ext.AutoRepr
class Config:
    def __init__(self):
        self.config_dir = CONFIG_DIR
        with (CONFIG_DIR / "base.yaml").open("r") as f:
            self.base_config = yaml.safe_load(f)
        self.cached: clc.OrderedDict = clc.OrderedDict()  # mypy weirdness

    @contextlib.contextmanager
    def of(self, ctx: Context):
        local_config_path: pl.Path = CONFIG_DIR / f"{ctx.identifier}.yaml"
        try:
            with local_config_path.open("r") as f:
                local_config = yaml.safe_load(f)
        except FileNotFoundError:
            local_config = {}

        combined_dict = {**self.base_config, **local_config}
        cleaned_dict = {k: combined_dict[k] for k in self.base_config}

        try:
            yield combined_dict
        finally:
            with local_config_path.open("w") as f:
                yaml.safe_dump(cleaned_dict, f)
