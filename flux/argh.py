from __future__ import annotations

import typing as ty
import dataclasses
import discord
import re

from .command import Command
from .config import Config
from .context import Context
from .errors import *
import argparse
import inspect
import sys

if ty.TYPE_CHECKING:
    from .context import Context
    from .flux import Flux


def MemberIDType(arg: str) -> int:
    match = re.search(r"<@?!?(\d*)>", arg)
    if not match:
        raise argparse.ArgumentError
    return int(match.group(1))


import traceback


class ArgumentParser(argparse.ArgumentParser):
    def _get_action_from_name(self, name):
        """Given a name, get the Action instance registered with this parser.
        If only it were made available in the ArgumentError object. It is
        passed as it's first arg...
        """
        container = self._actions
        if name is None:
            return None
        for action in container:
            if '/'.join(action.option_strings) == name:
                return action
            elif action.metavar == name:
                return action
            elif action.dest == name:
                return action

    def error(self, message):
        raise CommandError(message)

    def exit(self, status=0, message=None):
        raise CommandInfo(message)
if ty.TYPE_CHECKING:
    import discord
    from ._types import *


# p = argparse.ArgumentParser()
class JoinAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, " ".join(values))


def arghify(command: Command, skip=1) -> Command:
    func = command.func
    argparser = ArgumentParser()
    argparser.prog = f"{command.name}"

    func_params = list(inspect.signature(func).parameters.values())[skip:]
    # print(func_params)
    if help_doc := inspect.getdoc(func):
        help_doc = inspect.cleandoc(help_doc)
    for param in func_params:
        # print(type(param.annotation))
        # print(globals())
        param_annotation = eval(str(param.annotation))
        # print(param_annotation)
        if param.annotation is not inspect.Parameter.empty and isinstance(param_annotation := eval(param.annotation), Arg):
            # noinspection PyUnboundLocalVariable
            arg_dict: ty.Dict[str, ty.Any] = dataclasses.asdict(param_annotation)
            arg_dict["dest"] = param.name if param.name.startswith("-") else None
            names = arg_dict.pop("names", [])
            arg_dict_provided = {k: v for k, v in arg_dict.items() if v is not None}
            print(arg_dict_provided)
            argparser.add_argument(
                *names,
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
                if evaled_annotation in (str, int, float):
                    arg_dict["type"] = evaled_annotation
            argparser.add_argument(
                param.name,
                **arg_dict
            )
    command.short_usage = argparser.format_help().split("\n")[0].removeprefix("usage: ")
    command.argparser = argparser
    return command


@dataclasses.dataclass
class Arg:
    names: ty.Tuple = tuple()
    action: ty.Union[
        ty.Literal['store', 'store_const', 'store_true', 'store_false', 'append', 'append_const', 'count', 'help', 'version', 'extend'], ty.Type[argparse.Action]] = "store"
    nargs: ty.Optional[ty.Union[int, ty.Literal["?", "*", "_", "...", "+"]]] = None
    const = None
    default: ty.Union[ty.Any] = None
    type: ty.Optional[ty.Type, ty.Callable] = None
    choices: ty.Optional[ty.Tuple[str]] = None
    required: ty.Optional[bool] = None
    help: ty.Optional[str] = None
