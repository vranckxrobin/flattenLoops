# -----------------------------------------------------------------
# pycparser: using_cpp_libc.py
#
# Shows how to use the provided 'cpp' (on Windows, substitute for
# the 'real' cpp if you're on Linux/Unix) and "fake" libc includes
# to parse a file that includes standard C headers.
#
# Eli Bendersky [https://eli.thegreenplace.net/]
# License: BSD
# -----------------------------------------------------------------
import sys
from pycparser import c_ast

# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
#
sys.path.extend(['.', '..'])
declerations = []


def getDefaultValue(type):
    # TODO support other types if necessary
    return c_ast.Constant('string', "\"\"")


def typesForBlockItems(block):  # TODO add switch
    match type(block):
        case c_ast.Decl:
            global declerations
            declerations.append(block)
            return c_ast.Assignment('=', c_ast.ID(block.name), getDefaultValue(block.type))
        case c_ast.While:
            return c_ast.While(block.cond, blockItemsLoop(getattr(getattr(block, 'stmt', None), 'block_items', [])),
                               block.coord)
        case c_ast.DoWhile:
            return c_ast.DoWhile(block.cond, blockItemsLoop(getattr(getattr(block, 'stmt', None), 'block_items', [])),
                                 block.coord)
        case c_ast.If:
            return c_ast.If(block.cond, handleIfBody(block, 'iftrue'), handleIfBody(block, 'iffalse'), block.coord)
        case _:
            return block


def handleIfBody(block, ifCaseString):
    if isinstance(getattr(block, ifCaseString, None), c_ast.Compound):
        return c_ast.Compound(
            blockItemsLoop(getattr(getattr(block, ifCaseString, None), 'block_items', [])), block.coord)
    elif isinstance(getattr(block, ifCaseString, None), c_ast.If):
        return typesForBlockItems(getattr(block, ifCaseString, None))
    else:
        return getattr(block, ifCaseString, None)


def blockItemsLoop(block_items):
    return c_ast.Compound([typesForBlockItems(block) for block in block_items], None)

def allLocalVariablesToTopOfFunction(func):
    global declerations
    declerations = []
    funcBody = getattr(getattr(func, 'body', None), 'block_items', [])

    newBody = [typesForBlockItems(block) if c_ast.Decl != type(block) else block for block in funcBody]
    lastDecleration = next((i for i, x in enumerate(funcBody) if c_ast.Decl == type(x)), 0)
    newBody = c_ast.Compound(newBody[:lastDecleration] + declerations + newBody[lastDecleration:])

    return c_ast.FuncDef(func.decl, func.param_decls, newBody, None)

def allLocalVariablesAtTopOfFunctions(ast):
    return c_ast.FileAST([allLocalVariablesToTopOfFunction(func) for func in ast.ext])
