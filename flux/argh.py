from __future__ import annotations

import asyncio
import functools
import typing as ty
import dataclasses
import discord

from .command import Command
from .config import Config
from .context import Context
from .errors import *
import argparse
import inspect

if ty.TYPE_CHECKING:
    import discord
    from ._types import *


# p = argparse.ArgumentParser()


def argh(command: Command) -> Command:
    func = command.func
    argparser = argparse.ArgumentParser()

    func_params = list(inspect.signature(func).parameters.values())
    if help_doc := inspect.getdoc(func):
        help_doc = inspect.cleandoc(help_doc)
    for param in func_params:
        if param.annotation is not inspect.Parameter.empty and isinstance(param_annotation := eval(param.annotation), Arg):
            # noinspection PyUnboundLocalVariable
            arg_dict: ty.Dict[str, ty.Any] = dataclasses.asdict(param_annotation)
            aliases = [arg_name.replace("_", "-") for arg_name in list(arg_dict.pop("aliases", [])) + [func.__name__]]
            arg_dict_provided = {k: v for k, v in arg_dict.items() if v is not None}
            argparser.add_argument(
                *aliases,
                **arg_dict_provided
            )
        else:
            arg_dict = {}
            if param.default is not inspect.Parameter.empty:
                arg_dict["default"] = param.default
            if param.annotation is not inspect.Parameter.empty:
                if isinstance(evaled_annotation := eval(param.annotation), ty._GenericAlias):
                    if evaled_annotation.__origin__ is ty.Literal:
                        arg_dict["choices"] = evaled_annotation.__args__
                else:
                    arg_dict["type"] = eval(param.annotation)
            argparser.add_argument(
                param.name,
                **arg_dict
            )
    command.argparser = argparser
    return command


@dataclasses.dataclass
class Arg:
    aliases: ty.Tuple = tuple()
    action: ty.Union[ty.Literal['store', 'store_const', 'store_true', 'store_false', 'append', 'append_const', 'count', 'help', 'version', 'extend'], argparse.Action] = "store"
    nargs: ty.Optional[ty.Union[int, ty.Literal["?", "*", "_", "..."]]] = None
    const = None
    default: ty.Union[ty.Any] = None
    _type: ty.Optional[ty.Type] = None
    choices: ty.Optional[ty.Tuple[str]] = None
    required: ty.Optional[bool] = None
    help: ty.Optional[str] = None
