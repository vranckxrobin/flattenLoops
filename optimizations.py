from pycparser import c_ast


def replaceSwitch(ast, function):
    newAst = c_ast.FileAST([], ast.coord)
    for func in ast.ext:
        name = func.decl.name
        if name == function:
            functionBlocks = []
            for block in func.body.block_items:
                if type(block) == c_ast.While:
                    whileItems = []
                    for whileBlock in block.stmt.block_items:
                        if type(whileBlock) == c_ast.Switch:
                            cond = whileBlock.cond
                            for case in whileBlock.stmt.block_items:
                                caseBlocks = [
                                    tempBlock
                                    for tempBlock in case.stmts
                                    if type(tempBlock) != c_ast.Break
                                ]
                                whileItems.append(
                                    c_ast.If(c_ast.BinaryOp('==', cond, case.expr, None), c_ast.Compound(caseBlocks),
                                             None, None))
                        else:
                            whileItems.append(whileBlock)
                    functionBlocks.append(c_ast.While(block.cond, c_ast.Compound(whileItems)))
                else:
                    functionBlocks.append(block)
            newAst.ext.append(c_ast.FuncDef(func.decl, func.param_decls, c_ast.Compound(functionBlocks), None))
    return newAst
