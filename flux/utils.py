import ast
import time

import contextlib
import datetime


async def sexec(script: str, globals_=None, locals_=None):
    stmts = list(ast.iter_child_nodes(ast.parse(script)))
    if not stmts:
        return None
    if isinstance(stmts[-1], ast.Expr):
        if len(stmts) > 1:
            exec(compile(ast.Module(body=stmts[:-1], type_ignores=[]), filename="<ast>", mode="exec"), globals_, locals_)
        return eval(compile(ast.Expression(body=stmts[-1].value), filename="<ast>", mode="eval"), globals_, locals_)
    else:
        exec(script, globals_, locals_)

async def aexec(script: str, globals_=None, locals_=None):
    exec(
        f'async def __ex(): ' +
        ''.join(f'\n {l}' for l in script.split('\n')), globals_, locals_
    )
    return await locals()['__ex']()


class Timer:
    def __enter__(self):
        self.elapsed = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.elapsed
