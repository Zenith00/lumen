from __future__ import annotations

import typing as ty

if ty.TYPE_CHECKING:
    import discord
    from .context import Context
    from .type import *

import typing as ty
import inspect
import argparse

ParsingType = ty.Literal["argparse", "basic"]


class Command:
    def __init__(
            self,
            func: ContextFunction,
            parsing: ParsingType = "basic",

    ):
        self.func = func
        self.doc = inspect.getdoc(func)
        self.parsing = parsing
        if self.parsing == "argparse":
            self.argparser = argparse.ArgumentParser()

    async def execute(self, ctx: Context):
        return await self.func(ctx)


# noinspection PyShadowingBuiltins
def add_arg(self,
            command: Command,
            *name_or_flags: ty.Text,
            action: ty.Union[ty.Text, ty.Type[argparse.Action]] = None,
            nargs: ty.Union[int, ty.Text] = None,
            const: ty.Any = None,
            default: ty.Any = None,
            type: ty.Union[ty.Callable[[ty.Text], ty.Type], ty.Callable[[str], ty.Type], argparse.FileType] = None,
            choices: ty.Iterable[ty.Type] = None,
            required: bool = None,
            help: ty.Optional[ty.Text] = None,
            metavar: ty.Optional[ty.Union[ty.Text, ty.Tuple[ty.Text, None]]] = None,
            dest: ty.Optional[ty.Text] = None,
            version: ty.Text = None,
            **kwargs: ty.Any):
    if command.parsing != "argparse":
        raise TypeError("Attempted to add argparse arg to non-argparse command")
    command.argparser.add_argument(name_or_flags=name_or_flags, action=action, nargs=nargs, const=const, default=default, type=type, choices=choices,
                                   required=required, help=help, metavar=metavar, dest=dest, version=version, **kwargs)
    return command
