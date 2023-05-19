import sys
from pycparser import c_ast

sys.path.extend(['.', '..'])


# This function will add a decleration to the declarations variable.
def moveLocalVariables(stmt, declarations):  # TODO add switch
    match type(stmt):
        case c_ast.Decl:
            declarations.append(c_ast.Decl(stmt.name, None, None, None, None, stmt.type, None, None))
            if stmt.init is not None:
                return c_ast.Assignment('=', c_ast.ID(stmt.name), stmt.init)
        case c_ast.While:
            return c_ast.While(stmt.cond, blockItemsLoop(stmt.stmt.block_items, declarations))
        case c_ast.DoWhile:
            return c_ast.DoWhile(stmt.cond, blockItemsLoop(stmt.stmt.block_items, declarations))
        case c_ast.If:
            return c_ast.If(stmt.cond, handleIfBody(stmt, 'iftrue', declarations),
                            handleIfBody(stmt, 'iffalse', declarations))
        case _:
            return stmt


# handle a case(true case if ifCaseString is 'iftrue' or false case if ifCaseString is 'iffalse')
# of the if statement and call moveLocalVariables if necessary.
def handleIfBody(stmt, ifCaseString, declarations):
    if isinstance(getattr(stmt, ifCaseString), c_ast.Compound):
        return blockItemsLoop(getattr(getattr(stmt, ifCaseString), 'block_items', []), declarations)
    elif isinstance(getattr(stmt, ifCaseString), c_ast.If):
        return moveLocalVariables(getattr(stmt, ifCaseString), declarations)
    else:
        return getattr(stmt, ifCaseString)


def blockItemsLoop(block_items, declarations):
    return c_ast.Compound([moveLocalVariables(stmt, declarations) for stmt in block_items])


# Move all local variables for a function to the top
def allLocalVariablesToTopOfFunction(func):
    declarations = []
    funcBody = func.body.block_items if isinstance(func.body, c_ast.Compound) else []

    newBody = [stmt if isinstance(stmt, c_ast.Decl) else moveLocalVariables(stmt, declarations) for
               stmt in
               funcBody]

    return c_ast.FuncDef(func.decl, func.param_decls,
                         c_ast.Compound(declarations + newBody))


def allLocalVariablesToTopOfFunctions(ast):
    return c_ast.FileAST(
        [allLocalVariablesToTopOfFunction(func) for func in ast.ext if isinstance(func, c_ast.FuncDef)])
