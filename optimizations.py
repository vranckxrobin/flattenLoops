from pycparser import c_ast

def changeCaseToIf(cond, case):
    caseBlocks = [tempBlock for tempBlock in case.stmts if type(tempBlock) != c_ast.Break]
    return c_ast.If(c_ast.BinaryOp('==', cond, case.expr), c_ast.Compound(caseBlocks), None)


def replaceSwitch(ast, function: str):
    func = next(func for func in ast.ext if func.decl.name == function)
    whileIndex = next((i for i, block in enumerate(func.body.block_items) if isinstance(block, c_ast.While)), 0)
    whileLoop = func.body.block_items[whileIndex]
    switch = next(block for block in whileLoop.stmt.block_items if isinstance(block, c_ast.Switch))
    ifStatements = [changeCaseToIf(switch.cond, case) for case in switch.stmt.block_items]

    newFuncBody = func.body.block_items[:whileIndex] + [c_ast.While(whileLoop.cond, c_ast.Compound(ifStatements))]

    return c_ast.FileAST([c_ast.FuncDef(func.decl, func.param_decls, c_ast.Compound(newFuncBody))])
