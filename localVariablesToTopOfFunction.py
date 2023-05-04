import sys
from pycparser import c_ast

sys.path.extend(['.', '..'])


# This function will add a decleration to the declarations variable.
def moveLocalVariables(block, declarations):  # TODO add switch
    match type(block):
        case c_ast.Decl:
            declarations.append(block)
            return
        case c_ast.While:
            return c_ast.While(block.cond, blockItemsLoop(block.stmt.block_items, declarations))
        case c_ast.DoWhile:
            return c_ast.DoWhile(block.cond, blockItemsLoop(block.stmt.block_items, declarations))
        case c_ast.If:
            return c_ast.If(block.cond, handleIfBody(block, 'iftrue', declarations),
                            handleIfBody(block, 'iffalse', declarations))
        case _:
            return block


# handle a case(true case if ifCaseString is 'iftrue' or false case if ifCaseString is 'iffalse')
# of the if statement and call moveLocalVariables if necessary.
def handleIfBody(block: c_ast.If, ifCaseString: str, declarations):
    if isinstance(getattr(block, ifCaseString, None), c_ast.Compound):
        return c_ast.Compound(
            blockItemsLoop(getattr(getattr(block, ifCaseString, None), 'block_items', []), declarations), block.coord)
    elif isinstance(getattr(block, ifCaseString, None), c_ast.If):
        return moveLocalVariables(getattr(block, ifCaseString, None), declarations)
    else:
        return getattr(block, ifCaseString, None)


def blockItemsLoop(block_items, declarations):
    return c_ast.Compound([moveLocalVariables(block, declarations) for block in block_items])


# Move all local variables for a function to the top
def allLocalVariablesToTopOfFunction(func: c_ast.FuncDef):
    declarations = []
    funcBody = func.body.block_items if isinstance(func.body, c_ast.Compound) else []

    newBody = [block if isinstance(block, c_ast.Decl) else moveLocalVariables(block, declarations) for block in
               funcBody]

    return c_ast.FuncDef(func.decl, func.param_decls,
                         c_ast.Compound(declarations + newBody))


def allLocalVariablesToTopOfFunctions(ast: c_ast.FileAST):
    return c_ast.FileAST(
        [allLocalVariablesToTopOfFunction(func) for func in ast.ext if isinstance(func, c_ast.FuncDef)])
