import sys
from pycparser import c_ast

sys.path.extend(['.', '..'])
declerations = []


def getDefaultValue(type: c_ast.TypeDecl):
    # TODO support other types if necessary
    return c_ast.Constant('string', "\"\"")


# This function will add a decleration to the declerations variable.
# And it will change the decleration to an assignment with an initial value.
def moveLocalVariables(block):  # TODO add switch
    match type(block):
        case c_ast.Decl:
            global declerations
            declerations.append(block)
            return c_ast.Assignment('=', c_ast.ID(block.name), getDefaultValue(block.type))
        case c_ast.While:
            return c_ast.While(block.cond, blockItemsLoop(getattr(getattr(block, 'stmt', None), 'block_items', [])))
        case c_ast.DoWhile:
            return c_ast.DoWhile(block.cond, blockItemsLoop(getattr(getattr(block, 'stmt', None), 'block_items', [])))
        case c_ast.If:
            return c_ast.If(block.cond, handleIfBody(block, 'iftrue'), handleIfBody(block, 'iffalse'))
        case _:
            return block


# handle a case(true case if ifCaseString is 'iftrue' or false case if ifCaseString is 'iffalse')
# of the if statement and call moveLocalVariables if necessary.
def handleIfBody(block: c_ast.If, ifCaseString: str):
    if isinstance(getattr(block, ifCaseString, None), c_ast.Compound):
        return c_ast.Compound(
            blockItemsLoop(getattr(getattr(block, ifCaseString, None), 'block_items', [])), block.coord)
    elif isinstance(getattr(block, ifCaseString, None), c_ast.If):
        return moveLocalVariables(getattr(block, ifCaseString, None))
    else:
        return getattr(block, ifCaseString, None)


def blockItemsLoop(block_items):
    return c_ast.Compound([moveLocalVariables(block) for block in block_items])


# Move all local variables for a function to the top
def allLocalVariablesToTopOfFunction(func: c_ast.FuncDef):
    global declerations
    declerations = []
    funcBody = getattr(getattr(func, 'body', None), 'block_items', [])

    newBody = [moveLocalVariables(block) if c_ast.Decl != type(block) else block for block in funcBody]
    lastDecleration = next((i for i, x in enumerate(funcBody) if c_ast.Decl == type(x)), 0)

    return c_ast.FuncDef(func.decl, func.param_decls,
                         c_ast.Compound(newBody[:lastDecleration] + declerations + newBody[lastDecleration:]))


def allLocalVariablesAtTopOfFunctions(ast: c_ast.FileAST):
    return c_ast.FileAST(
        [allLocalVariablesToTopOfFunction(func) for func in ast.ext if isinstance(func, c_ast.FuncDef)])
