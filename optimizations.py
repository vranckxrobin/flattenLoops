from pycparser import c_ast


# Convert a switch case to an if statement
def changeCaseToIf(cond, case):
    caseBlocks = [tempBlock for tempBlock in case.stmts if type(tempBlock) != c_ast.Break]
    return c_ast.If(c_ast.BinaryOp('==', cond, case.expr), c_ast.Compound(caseBlocks), None)


# Find the switch and replace all case statements with if statements
def replaceSwitch(ast, function: str):
    # Find switch statement
    func = next(func for func in ast.ext if func.decl.name == function)
    whileIndex = next((i for i, block in enumerate(func.body.block_items) if isinstance(block, c_ast.While)), 0)
    whileLoop = func.body.block_items[whileIndex]
    switch = next(block for block in whileLoop.stmt.block_items if isinstance(block, c_ast.Switch))

    # Replace all case statements with if statements
    ifStatements = [changeCaseToIf(switch.cond, case) for case in switch.stmt.block_items]

    # Create the new function with the if statements
    newFuncBody = func.body.block_items[:whileIndex] + [c_ast.While(whileLoop.cond, c_ast.Compound(ifStatements))]
    return c_ast.FileAST([c_ast.FuncDef(func.decl, func.param_decls, c_ast.Compound(newFuncBody))])

#checks if the statement is a funcall to memcmp
def isMemcmp(statement):
    return isinstance(statement, c_ast.FuncCall) and statement.name.name == 'memcmp'

#transform memcmp into one that doesn't use loops can only tell if it is equal or not
def transformMemcmp(statement):
    compareTo=statement.args.exprs[1]
    result = c_ast.BinaryOp("==", c_ast.ArrayRef(statement.args.exprs[0],c_ast.Constant('int',str(0))), c_ast.Constant(compareTo.type,'\''+compareTo.value[1]+'\''))
    for x in range(1, int(statement.args.exprs[2].value)):
        compare = c_ast.BinaryOp("==", c_ast.ArrayRef(statement.args.exprs[0],c_ast.Constant('int',str(x))), c_ast.Constant(compareTo.type,'\''+compareTo.value[x+1]+'\''))
        result = c_ast.BinaryOp("&&", result, compare)
    return result

#find the memcmp statement
def findMemcmpStatement(statement):
    match type(statement):
        case c_ast.While:
            return c_ast.While(findMemcmpStatement(statement.cond),
                               c_ast.Compound(
                                   [findMemcmpStatement(tempBlock) for tempBlock in statement.stmt.block_items]))
        case c_ast.If:
            return c_ast.If(
                findMemcmpStatement(statement.cond), statement.iftrue, statement.iffalse)
        case c_ast.BinaryOp:
            if isMemcmp(statement.left): #check if the left statement is a function call to memcmp
                return transformMemcmp(statement.left) #transform mecmp to use no loops
            if isMemcmp(statement.right):
                return transformMemcmp(statement.right)
            return c_ast.BinaryOp(statement.op, findMemcmpStatement(statement.left), findMemcmpStatement(statement.right))
        case c_ast.Case:
            block_items = [findMemcmpStatement(tempBlock) for tempBlock in statement.stmts]
            return c_ast.Case(statement.expr, block_items)
        case _:  #
            return statement

#function that will replace the memcmp statement
def replaceMemcmp(ast, function):
    # Find switch statement
    func = next(func for func in ast.ext if func.decl.name == function)
    whileIndex = next((i for i, block in enumerate(func.body.block_items) if isinstance(block, c_ast.While)), 0)
    whileLoop = func.body.block_items[whileIndex]
    switch = next(block for block in whileLoop.stmt.block_items if isinstance(block, c_ast.Switch))

    #calls other function to find and transform the memcmp statement
    replaced = [c_ast.Case(case.expr, [findMemcmpStatement(statement) for statement in case.stmts]) for case in switch.stmt.block_items]

    # Create the new ast
    newFuncBody = func.body.block_items[:whileIndex] + [
        c_ast.While(whileLoop.cond, c_ast.Compound([c_ast.Switch(switch.cond, c_ast.Compound(replaced))]))]
    return c_ast.FileAST([c_ast.FuncDef(func.decl, func.param_decls, c_ast.Compound(newFuncBody))])

def optimize(ast,function):
    ast = replaceMemcmp(ast,function)
    return replaceSwitch(ast,function)
