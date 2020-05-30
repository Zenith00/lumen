import ast
import asyncio


def sexec(script: str, globals_=None, locals_=None):
    stmts = list(ast.iter_child_nodes(ast.parse(script)))
    if not stmts:
        return None
    if isinstance(stmts[-1], ast.Expr):
        if len(stmts) > 1:
            exec(compile(ast.Module(body=stmts[:-1]), filename="<ast>", mode="exec"), globals_, locals_)
        print(ast.Expression(body=stmts[-1].value))
        return eval(compile(ast.Expression(body=stmts[-1].value), filename="<ast>", mode="eval"), globals_, locals_)
    else:
        exec(script, globals_, locals_)


async def aexec(script: str, globals_=None, local_=None):
    exec(
        f'async def __ex(): ' +
        ''.join(f'\n {l}' for l in script.split('\n')), globals_, locals_
    )
    return await locals()['__ex']()


async def blah():
    print("blahing!")


async def mainy():
    sexec(
        """await blah()"""
    )


asyncio.run(mainy())
