from pycparser import c_ast


class DeclAndReplaceName:
    def __init__(self, decleration, name):
        self.decleration = decleration
        self.name = name


class DeclerationsAndAst(object):
    def __init__(self, declerations, func):
        self.declerations = declerations
        self.func = func
        self.currentCase = 0

    def getDeclerations(self):
        return self.declerations

    def getFunc(self):
        return self.func

    def setCase(self, currentCase):
        self.currentCase = currentCase

    def getCase(self):
        return self.currentCase


class InlineFunctions:
    def __init__(self, declerations, endOfSwitch, ast, returnToCase, functionVariableName):
        self.oldDeclerations = declerations
        self.newDeclerations = []
        self.endOfSwitch = endOfSwitch
        self.calls = []
        self.ast = ast  # TODO use this ast instead of passing it around
        self.currentCase = 0
        self.first = True
        self.returnToCase = returnToCase
        self.functionVariableName = functionVariableName
        self.previousEndOfSwitch = 0
        self.functionCallParameters = []
        self.firstCase = True
        self.replaceVariable = []

    def setPreviousEndOfSwitch(self, endOfSwitch):
        self.previousEndOfSwitch = endOfSwitch

    # TODO set the parameterVariable to the one calling this (example bool x= parsealt(p->xml) -> param_p = p->xml;x=parsealt)
    # TODO check if parameter already declared in normal function and rename them(after renaiming check again)
    # TODO check if local variable are already declared and rename them if they have the same name(after renaiming check again)
    def changesDeclaredVariables(self, func, functionName):
        for block in func.body.block_items:
            if type(block) == c_ast.Decl:
                if not self.isInOldDeclerations(block):
                    self.newDeclerations.append(block)
                else:
                    if block.name != 'run' and block.name != 'programStep':
                        self.replaceVariableAndDeclare(block)

    def blockReplaceDeclName(self, block, name):
        if hasattr(block, 'declname'):
            block.declname = name
            return block
        else:
            block.type = self.blockReplaceDeclName(block.type, name)
            return block

    def replaceVariableAndDeclare(self, block):
        name = block.name
        name += "_2"
        while self.isInOldOrNewDeclerations(name):
            name += "_2"
        # block.type.type.declname=name #TODO check if this is correct for other types
        block = self.blockReplaceDeclName(block, name)
        block.name = name
        self.newDeclerations.append(block)
        self.replaceVariable.append(DeclAndReplaceName(block.name, name))

    def isInOldDeclerations(self, block):
        for decl in self.oldDeclerations:
            if decl.name == block.name:
                return True
        return False

    def isInOldOrNewDeclerations(self, name):
        for decl in self.oldDeclerations:
            if decl.name == name:
                return True
        for decl in self.newDeclerations:
            if decl.name == name:
                return True
        return False

    # TODO make it possible for multiple functions calls (now only one)
    # TODO inline multiple functions  now start with (inlining parseelt of minixml)
    # TODO ceck for infinite loops like function parseXML to parseelt to parseatt back to parseXML and fix this
    def inlineFunctions(self, ast, functionName):
        func = None
        for func in ast.ext:
            name = func.decl.name
            if name == functionName:
                self.functionParams = getattr(func.decl.type.args, 'params',
                                              [])
                self.declareParameters()

                self.changesDeclaredVariables(func, functionName)
                func = self.findFunctionCallsAndInlineOtherFunctions(ast, func, functionName)
                func = self.changeProgramStepAndReturn(func, functionName)
                break
        return DeclerationsAndAst(self.newDeclerations, func)

    # TODO check todos inlineFunctions maybe needed here
    def findFunctionCallsAndInlineOtherFunctions(self, ast, func, function):
        self.returnTypeOfFunction = func.decl.type.type.type.names[0]
        block_items = []
        for block in func.body.block_items:
            block_items.append(self.findCalls(block))
        tmpFunc = c_ast.FuncDef(func.decl, func.param_decls, c_ast.Compound(block_items))
        return self.inlineFunction(tmpFunc)


    def changeCall(self, function, functionVariableName, parameters):
        endOfSwitch = self.endOfSwitch + self.numberOfCases - self.endOfSwitch  # TODO set amount of cases in this function
        returnToCase = self.currentCase + self.endOfSwitch
        declerationsArr = []
        declerationsArr.extend(self.oldDeclerations)
        declerationsArr.extend(self.newDeclerations)
        inlineFunctions = InlineFunctions(declerationsArr, endOfSwitch, self.ast, returnToCase, functionVariableName)
        inlineFunctions.setPreviousEndOfSwitch(self.endOfSwitch)
        inlineFunctions.setCallerParameters(parameters)
        result = inlineFunctions.inlineFunctions(self.ast, function)
        result.setCase(self.currentCase)
        self.calls.append(result)

        self.newDeclerations.extend(result.getDeclerations())

    def findCalls(self, block):
        match type(block):
            case c_ast.FuncCall:  # TODO call this class again for the other function to flatten and add it to this one
                if self.functionInFile(block.name.name):
                    name = self.appendDecleration(block.name.name)
                    self.changeCall(block.name.name, name, block.args.exprs)
                    return c_ast.ID(name)
                else:
                    return block
            case c_ast.While:
                cond = self.findCalls(block.cond)
                block_items = []
                for tempBlock in block.stmt.block_items:
                    block_items.append(self.findCalls(tempBlock))
                stmt = c_ast.Compound(block_items)
                return c_ast.While(cond, stmt)
            case c_ast.If:
                cond = self.findCalls(block.cond)
                block_items_true_case = []
                block_items_false_case = []
                if c_ast.Compound == type(block.iftrue):
                    for tempBlock in block.iftrue.block_items:
                        block_items_true_case.append(self.findCalls(tempBlock))
                elif c_ast.If == type(block.iftrue):
                    block_items_true_case.append(self.findCalls(block.iftrue))
                else:
                    block_items_true_case.append(self.findCalls(block.iftrue))

                if c_ast.Compound == type(block.iffalse):
                    for tempBlock in block.iffalse.block_items:
                        block_items_false_case.append(self.findCalls(tempBlock))
                elif c_ast.If == type(block.iffalse):
                    block_items_false_case.append(self.findCalls(block.iffalse))
                else:
                    block_items_false_case.append(self.findCalls(block.iffalse))
                return c_ast.If(cond, c_ast.Compound(block_items_true_case), c_ast.Compound(block_items_false_case))
            case c_ast.Case:
                self.currentCase = int(block.expr.value)
                cond = self.findCalls(block.expr)
                block_items = []
                if self.firstCase:
                    self.firstCase = False
                    i = 0
                    for param in self.functionCallParameters:
                        block_items.append(c_ast.Assignment('=', c_ast.ID(self.functionParams[i].name), param))
                        i += 1

                    # TODO set parameters self.functionCallParameters
                for tempBlock in block.stmts:
                    block_items.append(self.findCalls(tempBlock))
                return c_ast.Case(cond, block_items)
            case c_ast.Switch:
                if self.first:
                    self.first = False
                    self.numberOfCases = int(block.stmt.block_items[-1].expr.value)
                cond = self.findCalls(block.cond)
                block_items = []
                for tempBlock in block.stmt.block_items:
                    block_items.append(self.findCalls(tempBlock))
                return c_ast.Switch(cond, c_ast.Compound(block_items))
            case _:  #
                return block

    def replaceProgramStepAndReturn(self, block):
        valueToAdd = self.endOfSwitch
        if self.calls.__len__() >0:
            pass
        match type(block):
            case c_ast.Assignment:
                if block.lvalue.name == 'programStep':
                    valueToAdd = int(block.rvalue.value) + valueToAdd
                    for call in self.calls:
                        if call.getCase() == int(block.rvalue.value):
                            valueToAdd = self.numberOfCases + 1 + self.endOfSwitch  # TODO this one is to move to the function but if there are multiple function calls then this likely wouldn't work
                            break
                    return c_ast.Assignment(block.op, block.lvalue, c_ast.Constant(block.rvalue.type, str(valueToAdd)))
                else:
                    return c_ast.Assignment(block.op, self.replaceProgramStepAndReturn(block.lvalue),
                                            self.replaceProgramStepAndReturn(block.rvalue))  # original  return block
            case c_ast.Return:
                block_items = []
                nameOfFunctionThatWasCalled = self.functionVariableName
                jumpBack = self.returnToCase
                if self.returnTypeOfFunction != 'void':
                    value = block.expr
                    block_items.append(c_ast.Assignment('=', c_ast.ID(nameOfFunctionThatWasCalled), value))
                block_items.append(c_ast.Assignment('=', c_ast.ID('programStep'), c_ast.Constant('int', str(jumpBack))))
                return c_ast.Compound(block_items)
            case c_ast.While:
                block_items = []
                for tempBlock in block.stmt.block_items:
                    block_items.append(self.replaceProgramStepAndReturn(tempBlock))
                stmt = c_ast.Compound(block_items)
                return c_ast.While(self.replaceProgramStepAndReturn(block.cond), stmt)
            case c_ast.If:
                block_items_true_case = []
                block_items_false_case = []
                if c_ast.Compound == type(block.iftrue):
                    for tempBlock in block.iftrue.block_items:
                        block_items_true_case.append(self.replaceProgramStepAndReturn(tempBlock))
                elif c_ast.If == type(block.iftrue):
                    block_items_true_case.append(self.replaceProgramStepAndReturn(block.iftrue))
                else:
                    block_items_true_case.append(self.replaceProgramStepAndReturn(block.iftrue))

                if c_ast.Compound == type(block.iffalse):
                    for tempBlock in block.iffalse.block_items:
                        block_items_false_case.append(self.replaceProgramStepAndReturn(tempBlock))
                elif c_ast.If == type(block.iffalse):
                    block_items_false_case.append(self.replaceProgramStepAndReturn(block.iffalse))
                else:
                    block_items_false_case.append(self.replaceProgramStepAndReturn(block.iffalse))
                return c_ast.If(self.replaceProgramStepAndReturn(block.cond), c_ast.Compound(block_items_true_case),
                                c_ast.Compound(block_items_false_case))
            case c_ast.Case:
                block.expr.value = str(int(block.expr.value) + valueToAdd)
                block_items = []
                if getattr(getattr(block.stmts[0], 'lvalue', None), 'name',
                           "") == "run" and self.endOfSwitch != 0:
                    jumpBack = self.returnToCase
                    block_items.append(c_ast.Compound([c_ast.Assignment('=', c_ast.ID('programStep'),
                                                                        c_ast.Constant('int',
                                                                                       str(jumpBack)))]))  # TODO is a hack should be implemented better but in this code programStep in Compound won't get updated (unless in the usual place like in if and while) #TODO test removed ,c_ast.Break(None)
                else:
                    for tempBlock in block.stmts:
                        block_items.append(self.replaceProgramStepAndReturn(tempBlock))
                return c_ast.Case(block.expr, block_items)
            case c_ast.Switch:
                block_items = []
                for tempBlock in block.stmt.block_items:
                    block_items.append(self.replaceProgramStepAndReturn(tempBlock))
                return c_ast.Switch(block.cond, c_ast.Compound(block_items))
            case c_ast.BinaryOp:
                return c_ast.BinaryOp(block.op, self.replaceProgramStepAndReturn(block.left),
                                      self.replaceProgramStepAndReturn(block.right))
            case c_ast.UnaryOp:
                return c_ast.UnaryOp(block.op, self.replaceProgramStepAndReturn(block.expr))
            case c_ast.StructRef:
                return c_ast.StructRef(self.replaceProgramStepAndReturn(block.name), block.type, block.field)
            case c_ast.ID:
                for x in self.replaceVariable:
                    if x.decleration == block.name:
                        return c_ast.ID(x.name)
                return block
            case c_ast.Decl:
                for x in self.replaceVariable:
                    if x.decleration == block.name:
                        return c_ast.Decl(x.name, block.quals, block.align, block.storage, block.funcspec, block.type,
                                          block.init, block.bitsize, block.coord)
                return block
            case _:
                return block

    def changeProgramStepAndReturn(self, func,
                                   function):
        block_items = []
        for block in func.body.block_items:
            block_items.append(self.replaceProgramStepAndReturn(block))
        tmpFunc = c_ast.FuncDef(func.decl, func.param_decls, c_ast.Compound(block_items))
        return tmpFunc

    def appendDecleration(self, name):
        # TODO check for no conflict with already declared variables or variables in the newDeclrations
        decl = c_ast.Decl(name, None, None, None, None, c_ast.TypeDecl(name, None, None, c_ast.IdentifierType(['int'])),
                          None,
                          None)  # TODO replace int with actually function return value if void don't add this variable
        self.newDeclerations.append(decl)
        return name

    def functionInFile(self, function):
        for func in self.ast.ext:
            name = func.decl.name
            if name == function:
                return True
        return False

    def inlineFunction(self, func):
        block_items = []
        block_items.extend(self.newDeclerations)

        for block in func.body.block_items:
            if type(block) == c_ast.While:  # TODO more concrete check can check that it is actually while(run)  #old not first and type(block)==c_ast.While
                block_items_while = []
                for tempBlock in block.stmt.block_items:
                    block_items_switch = []
                    if type(tempBlock) == c_ast.Switch:
                        lenSwitch = len(tempBlock.stmt.block_items)
                        for i in range(lenSwitch):
                            if i == (lenSwitch - 1):
                                for call in self.calls:
                                    for tempCallBlock in call.getFunc().body.block_items:
                                        if type(tempCallBlock) == c_ast.While:
                                            for tempCallBlockWhile in tempCallBlock.stmt.block_items:
                                                if type(tempCallBlockWhile) == c_ast.Switch:
                                                    block_items_switch.extend(tempCallBlockWhile.stmt.block_items)
                                block_items_switch.append(tempBlock.stmt.block_items[
                                                                  i])
                            else:
                                block_items_switch.append(tempBlock.stmt.block_items[i])
                        block_items_while.append(c_ast.Switch(tempBlock.cond, c_ast.Compound(block_items_switch)))
                    else:
                        block_items_while.append(tempBlock)
                block_items.append(c_ast.While(block.cond, c_ast.Compound(block_items_while)))
        tmpFunc = c_ast.FuncDef(func.decl, func.param_decls, c_ast.Compound(block_items))
        return tmpFunc

    def setCallerParameters(self, parameters):
        self.functionCallParameters = parameters

    def declareParameters(self):
        if self.functionCallParameters.__len__() != 0:
            for functionParam in self.functionParams:
                if not any(x.name == functionParam.name for x in
                           self.oldDeclerations):  # TODO else case change to toher value and change the variable of the function to be inlined
                    self.newDeclerations.append(
                        c_ast.Decl(functionParam.name, None, None, None, None, functionParam.type, None, None,
                                   None))
                else:
                    self.replaceVariableAndDeclare(functionParam)


def inlineFunctions(ast, function):
    inlineFuncClass = InlineFunctions([], 0, ast, 0, '')
    declerationsAndFunc = inlineFuncClass.inlineFunctions(ast, function)
    ast.ext = [declerationsAndFunc.getFunc()]
    return ast
