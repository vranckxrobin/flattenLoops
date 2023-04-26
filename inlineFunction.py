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
        self.parameters = []
        self.oldDeclerations = declerations
        self.newDeclerations = []
        self.endOfSwitch = endOfSwitch
        self.calls = []
        self.ast = ast  # TODO use this ast instead of passing it around
        self.currentCase = 0
        self.returnToCase = returnToCase
        self.functionVariableName = functionVariableName
        self.functionCallParameters = []
        # self.firstCase = True
        self.replaceVariable = []
        self.callerFunctionParameters = []

    # TODO set the parameterVariable to the one calling this (example bool x= parsealt(p->xml) -> param_p = p->xml;x=parsealt)
    # TODO check if parameter already declared in normal function and rename them(after renaiming check again)
    # TODO check if local variable are already declared and rename them if they have the same name(after renaiming check again)
    def changesDeclaredVariables(self, func):
        for block in func.body.block_items:
            if type(block) == c_ast.Decl:
                if not self.isInOldDeclerations(block.name):
                    self.newDeclerations.append(block)
                elif block.name not in ['run', 'programStep']:
                    self.replaceVariableAndDeclare(block)

    def blockReplaceDeclName(self, block, name):
        if hasattr(block, 'declname'):
            block.declname = name
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
        return name

    def isInOldDeclerations(self, name):
        return any(decl.name == name for decl in self.oldDeclerations)

    def isInOldOrNewDeclerations(self, name):
        return self.isInOldDeclerations(name) or any(decl.name == name for decl in self.newDeclerations)

    def inlineFunction(self, func):
        self.functionParams = getattr(func.decl.type.args, 'params',
                                      [])
        self.declareParameters()
        self.changesDeclaredVariables(func)
        func = self.findFunctionCallsAndInlineOtherFunctions(func)
        return self.changeProgramStepAndReturn(func)

    # TODO make it possible for multiple functions calls (now only one)
    # TODO inline multiple functions  now start with (inlining parseelt of minixml)
    # TODO ceck for infinite loops like function parseXML to parseelt to parseatt back to parseXML and fix this
    def inlineFunctions(self, functionName):
        func = next(func for func in self.ast.ext if func.decl.name == functionName)
        return DeclerationsAndAst(self.newDeclerations, self.inlineFunction(func))

    # TODO check todos inlineFunctions maybe needed here
    def findFunctionCallsAndInlineOtherFunctions(self, func):
        self.returnTypeOfFunction = func.decl.type.type.type.names[0]
        block_items = [self.findCalls(block) for block in func.body.block_items]
        tmpFunc = c_ast.FuncDef(func.decl, func.param_decls, c_ast.Compound(block_items))
        return self.inlineFunctionCall(tmpFunc)

    def changeCall(self, function, functionVariableName, parameters):
        endOfSwitch = self.endOfSwitch + self.numberOfCases - self.endOfSwitch  # TODO set amount of cases in this function
        returnToCase = self.currentCase + self.endOfSwitch
        declerationsArr = self.oldDeclerations + self.newDeclerations

        inlineFunctions = InlineFunctions(declerationsArr, endOfSwitch, self.ast, returnToCase, functionVariableName)
        inlineFunctions.setCallerParameters(parameters)

        result = inlineFunctions.inlineFunctions(function)
        result.setCase(self.currentCase)
        self.callerFunctionParameters = inlineFunctions.getParameters()
        self.calls.append(result)
        self.newDeclerations.extend(result.getDeclerations())

    def ifBodyCase(self, ifBodyCase):
        if isinstance(ifBodyCase, c_ast.Compound):
            return [self.findCalls(tempBlock) for tempBlock in ifBodyCase.block_items]
        else:
            return [self.findCalls(ifBodyCase)]

    def findCalls(self, block):
        match type(block):
            case c_ast.FuncCall:  # TODO call this class again for the other function to flatten and add it to this one
                if not self.functionInFile(block.name.name):
                    return block
                name = self.appendDecleration(block.name.name)
                self.changeCall(block.name.name, name, block.args.exprs)
                return c_ast.ID(name)
            case c_ast.While:
                return c_ast.While(self.findCalls(block.cond),
                                   c_ast.Compound([self.findCalls(tempBlock) for tempBlock in block.stmt.block_items]))
            case c_ast.If:
                return c_ast.If(
                    self.findCalls(block.cond),
                    c_ast.Compound(self.ifBodyCase(block.iftrue)),
                    c_ast.Compound(self.ifBodyCase(block.iffalse)))
            case c_ast.Case:
                self.currentCase = int(block.expr.value)
                block_items = []
                # if self.firstCase:
                #     self.firstCase = False
                #     block_items = [c_ast.Assignment('=', c_ast.ID(self.functionParams[i].name), param) for i, param in
                #                    enumerate(self.functionCallParameters)]
                block_items += [self.findCalls(tempBlock) for tempBlock in block.stmts]
                return c_ast.Case(self.findCalls(block.expr), block_items)
            case c_ast.Switch:
                self.numberOfCases = int(block.stmt.block_items[-1].expr.value)
                return c_ast.Switch(self.findCalls(block.cond),
                                    c_ast.Compound([self.findCalls(tempBlock) for tempBlock in block.stmt.block_items]))
            case _:  #
                return block

    def replaceProgramStepAndReturnIfCase(self, ifBodyCase):
        if isinstance(ifBodyCase, c_ast.Compound):
            return [self.replaceProgramStepAndReturn(tempBlock) for tempBlock in ifBodyCase.block_items]
        else:
            return [self.replaceProgramStepAndReturn(ifBodyCase)]

    def replaceProgramStepAndReturn(self, block):
        valueToAdd = self.endOfSwitch
        if self.calls.__len__() > 0:
            pass
        match type(block):
            case c_ast.Assignment:
                if block.lvalue.name != 'programStep':
                    return c_ast.Assignment(
                        block.op,
                        self.replaceProgramStepAndReturn(block.lvalue),
                        self.replaceProgramStepAndReturn(block.rvalue),
                    )  # original  return block
                self.setParams = (
                            self.setParams or any(call.getCase() == int(block.rvalue.value) for call in self.calls))
                valueToAdd = self.numberOfCases + 1 + self.endOfSwitch if any(
                    call.getCase() == int(block.rvalue.value) for call in self.calls) else valueToAdd + int(
                    block.rvalue.value)
                return c_ast.Assignment(
                    block.op,
                    block.lvalue,
                    c_ast.Constant(block.rvalue.type, str(valueToAdd)),
                )
            case c_ast.Return:
                block_items = [
                    c_ast.Assignment('=', c_ast.ID('programStep'), c_ast.Constant('int', str(self.returnToCase)))]
                if self.returnTypeOfFunction != 'void':
                    block_items = [c_ast.Assignment('=', c_ast.ID(self.functionVariableName), block.expr)] + block_items
                return c_ast.Compound(block_items)
            case c_ast.While:
                return c_ast.While(
                    self.replaceProgramStepAndReturn(block.cond), c_ast.Compound(
                        [self.replaceProgramStepAndReturn(tempBlock) for tempBlock in block.stmt.block_items])
                )
            case c_ast.If:
                return c_ast.If(
                    self.replaceProgramStepAndReturn(block.cond),
                    c_ast.Compound(self.replaceProgramStepAndReturnIfCase(block.iftrue)),
                    c_ast.Compound(self.replaceProgramStepAndReturnIfCase(block.iffalse)))
            case c_ast.Case:
                self.setParams = False
                block.expr.value = str(int(block.expr.value) + valueToAdd)
                if getattr(getattr(block.stmts[0], 'lvalue', None), 'name', "") == "run" and self.endOfSwitch != 0:
                    block_items = [c_ast.Compound([c_ast.Assignment('=', c_ast.ID('programStep'), c_ast.Constant('int',
                                                                                                                 str(self.returnToCase)), )])]  # TODO is a hack should be implemented better but in this code programStep in Compound won't get updated (unless in the usual place like in if and while) #TODO test removed ,c_ast.Break(None)
                else:
                    block_items = [self.replaceProgramStepAndReturn(tempBlock) for tempBlock in block.stmts]
                if self.setParams:
                    block_items = block_items[:(len(block_items) - 2)] + \
                                  [c_ast.Assignment('=', c_ast.ID(param), c_ast.ID(self.functionParams[i].name)) for
                                   i, param in
                                   enumerate(self.callerFunctionParameters)] + block_items[len(block_items) - 2:]
                return c_ast.Case(block.expr, block_items)
            case c_ast.Switch:
                return c_ast.Switch(block.cond, c_ast.Compound(
                    [self.replaceProgramStepAndReturn(tempBlock) for tempBlock in block.stmt.block_items]))
            case c_ast.BinaryOp:
                return c_ast.BinaryOp(
                    block.op,
                    self.replaceProgramStepAndReturn(block.left),
                    self.replaceProgramStepAndReturn(block.right),
                )
            case c_ast.UnaryOp:
                return c_ast.UnaryOp(
                    block.op, self.replaceProgramStepAndReturn(block.expr)
                )
            case c_ast.StructRef:
                return c_ast.StructRef(
                    self.replaceProgramStepAndReturn(block.name),
                    block.type,
                    block.field,
                )
            case c_ast.ID:
                return next((c_ast.ID(x.name) for x in self.replaceVariable if x.decleration == block.name), block)
            case c_ast.Decl:
                return next((c_ast.Decl(
                    x.name,
                    block.quals,
                    block.align,
                    block.storage,
                    block.funcspec,
                    block.type,
                    block.init,
                    block.bitsize,
                ) for x in self.replaceVariable if x.decleration == block.name
                ), block)
            case _:
                return block

    def changeProgramStepAndReturn(self, func):
        return c_ast.FuncDef(func.decl, func.param_decls, c_ast.Compound(
            [self.replaceProgramStepAndReturn(block) for block in func.body.block_items]))

    def appendDecleration(self, name):
        # TODO check for no conflict with already declared variables or variables in the newDeclrations
        decl = c_ast.Decl(name, None, None, None, None, c_ast.TypeDecl(name, None, None, c_ast.IdentifierType(['int'])),
                          None,
                          None)  # TODO replace int with actually function return value if void don't add this variable
        self.newDeclerations.append(decl)
        return name

    def functionInFile(self, function):
        return any(func.decl.name == function for func in self.ast.ext)

    def getSwitchCasesFromCall(self, call):
        functionWhileLoop = next(
            block for block in call.getFunc().body.block_items if isinstance(block, c_ast.While))
        functionSwitch = next(
            tempCallBlockWhile for tempCallBlockWhile in functionWhileLoop.stmt.block_items if
            isinstance(tempCallBlockWhile, c_ast.Switch))
        return functionSwitch.stmt.block_items

    def flatten(self, list):
        return [element for sublist in list for element in sublist]

    def inlineFunctionCall(self, func):
        whileLoop = next(block for block in func.body.block_items if type(block) == c_ast.While)
        switch = next(block for block in whileLoop.stmt.block_items if isinstance(block, c_ast.Switch))

        lenSwitch = len(switch.stmt.block_items) - 1
        block_items_switch = switch.stmt.block_items[:lenSwitch] + \
                             self.flatten([self.getSwitchCasesFromCall(call) for call in self.calls]) + \
                             [switch.stmt.block_items[lenSwitch]]

        block_items = self.newDeclerations + [c_ast.While(whileLoop.cond,
                                                          c_ast.Compound([c_ast.Switch(switch.cond, c_ast.Compound(
                                                              block_items_switch))]))]
        return c_ast.FuncDef(func.decl, func.param_decls, c_ast.Compound(block_items))

    def setCallerParameters(self, parameters):
        self.functionCallParameters = parameters

    def getParameters(self):
        return self.parameters

    def declareParameters(self):
        if self.functionCallParameters.__len__() != 0:
            for functionParam in self.functionParams:
                if all(x.name != functionParam.name for x in self.oldDeclerations):
                    name = functionParam.name
                    self.newDeclerations.append(
                        c_ast.Decl(functionParam.name, None, None, None, None, functionParam.type, None, None))
                else:
                    name = self.replaceVariableAndDeclare(functionParam)
                self.parameters.append(name)


def inlineFunctions(ast, function):
    inlineFuncClass = InlineFunctions([], 0, ast, 0, '')
    declerationsAndFunc = inlineFuncClass.inlineFunctions(function)
    return c_ast.FileAST([declerationsAndFunc.getFunc()])
