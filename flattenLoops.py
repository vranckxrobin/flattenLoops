import sys

from pycparser import c_ast
import copy

sys.path.extend(['.', '..'])


class FlattenPart:
    def __init__(self, block, currentCaseNumber, returnToCase):
        self.currentCaseNumber = currentCaseNumber
        self.returnToCase = returnToCase  # TODO Note if zero no returnStatement
        self.cases = []
        self.caseNumber = currentCaseNumber
        self.callsFunctionNotInFile = False
        self.flattenCaseByType(block)

    def getCurrentCaseNumber(self):
        return self.currentCaseNumber

    def getCases(self):
        return self.cases

    def transformWhileBodyToCases(self, block, returnToWhile):
        lengthBlock_items = len(block.stmt.block_items) - 1
        for pos, tempBlock in enumerate(block.stmt.block_items):
            returnToCase = returnToWhile if pos == lengthBlock_items else 0
            flattenPart = FlattenPart(tempBlock, self.currentCaseNumber, returnToCase)
            self.cases.extend(flattenPart.getCases())
            self.currentCaseNumber = flattenPart.getCurrentCaseNumber()

    def transformWhileConditionToIf(self, block, caseNumber, returnToCase, nextInstruction):
        falseCase = [c_ast.Assignment("=", c_ast.ID("programStep", None),
                                      c_ast.Constant("int", str(returnToCase), None),
                                      None)]

        case = [
            c_ast.If(
                block.cond,
                c_ast.Compound(
                    [
                        c_ast.Assignment(
                            "=",
                            c_ast.ID("programStep", None),
                            c_ast.Constant("int", str(nextInstruction), None),
                            None,
                        )
                    ]
                ),
                c_ast.Compound(falseCase),
                None,
            ),
            c_ast.Break(None),
        ]
        self.cases.append(
            c_ast.Case(c_ast.Constant("int", str(caseNumber), None), case,
                       None))  # programstep of this case (tmpCaseCount)

    def handleWhileCase(self, block):
        self.currentCaseNumber = self.currentCaseNumber + 1
        nextInstruction = self.currentCaseNumber
        self.transformWhileBodyToCases(block, self.caseNumber)
        returnToCase = self.returnToCase if self.returnToCase != 0 else self.currentCaseNumber
        self.transformWhileConditionToIf(block, self.caseNumber, returnToCase, nextInstruction)

    def handleDoWhileCase(self, block):
        nextInstruction = self.currentCaseNumber
        self.transformWhileBodyToCases(block, 0)
        returnToCase = self.returnToCase if self.returnToCase != 0 else self.currentCaseNumber + 1
        self.transformWhileConditionToIf(block, self.currentCaseNumber, returnToCase, nextInstruction)
        self.currentCaseNumber = self.currentCaseNumber + 1

    def handleIfCase(self, block):
        saveSelf = copy.deepcopy(self)
        self.currentCaseNumber += 1
        self.handleIfBody(block, 'iftrue')
        self.handleIfBody(block, 'iffalse')

        returnToCase = self.returnToCase if self.returnToCase != 0 else self.currentCaseNumber

        # TODO reset self do truecase and false case aagain but now for the truecase with the returning of the if function
        self.currentCaseNumber = saveSelf.currentCaseNumber
        self.cases = saveSelf.cases
        self.returnToCase = saveSelf.returnToCase
        self.caseNumber = saveSelf.caseNumber

        self.returnToCase = returnToCase
        self.callsFunctionNotInFile = False

        self.currentCaseNumber += 1
        trueCase = self.handleIfBody(block, 'iftrue')
        self.returnToCase = saveSelf.returnToCase
        falseCase = self.handleIfBody(block, 'iffalse')

        if falseCase is None and not self.callsFunctionNotInFile:
            falseCase = c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep", None),
                                                         c_ast.Constant("int", str(returnToCase), None),
                                                         None)])  # point to what is outside the loop (returnToCase)

        case = [c_ast.If(block.cond, trueCase, falseCase, None)]
        if self.callsFunctionNotInFile:
            case.append(c_ast.Assignment("=", c_ast.ID("programStep", None),
                                         c_ast.Constant("int", str(returnToCase), None),
                                         None))  # point to what is outside the loop (returnToCase)
        case.append(c_ast.Break(None))
        self.cases.append(
            c_ast.Case(c_ast.Constant("int", str(self.caseNumber), None), case,
                       None))  # programstep of this case (self.caseNumber)

    def handleDefault(self, block):
        self.currentCaseNumber += 1
        returnToCase = (
            self.returnToCase if self.returnToCase != 0 else self.currentCaseNumber
        )
        temp = [block, c_ast.Assignment(
            "=",
            c_ast.ID("programStep", None),
            c_ast.Constant("int", str(returnToCase), None),
            None,
        ), c_ast.Break(None)]
        self.cases.append(
            c_ast.Case(c_ast.Constant("int", str(self.caseNumber), None), temp,
                       None))

    def flattenCaseByType(self, block):
        match type(block):  # TODO add switch
            case c_ast.While:  # TODO createDoWhile and if
                self.handleWhileCase(block)
            case c_ast.DoWhile:  # TODO check if if else is correct
                self.handleDoWhileCase(block)
            case c_ast.If:
                self.handleIfCase(block)
            case _:  #
                self.handleDefault(block)

    def needsFlattening(self, param):
        return param in [c_ast.While, c_ast.If, c_ast.DoWhile]

    def createCase(self, operations, returnToCase):
        tmpCaseNumber = self.currentCaseNumber
        self.currentCaseNumber += 1
        returnToCase = returnToCase if returnToCase != 0 else self.currentCaseNumber
        operations.append(c_ast.Assignment("=", c_ast.ID("programStep", None),
                                           c_ast.Constant("int", str(returnToCase), None),
                                           None))
        operations.append(c_ast.Break(None))
        self.cases.append(
            c_ast.Case(c_ast.Constant("int", str(tmpCaseNumber), None), operations,
                       None))

    def createCasesForIfBody(self,ifcase):
        creatingCase = False
        temp = []
        lengthBlock_items = len(ifcase.block_items.block_items) - 1
        for pos, tempBlock in enumerate(ifcase.block_items.block_items):
            if self.needsFlattening(type(tempBlock)):
                if creatingCase:
                    creatingCase = False
                    self.createCase(temp, 0)
                    temp = []
                returnToCase = self.returnToCase if pos == lengthBlock_items else 0
                flattenPart = FlattenPart(tempBlock, self.currentCaseNumber,
                                          returnToCase)
                self.cases.extend(flattenPart.getCases())
                self.currentCaseNumber = flattenPart.getCurrentCaseNumber()
            else:
                creatingCase = True
                temp.append(tempBlock)
        if creatingCase:
            self.createCase(temp, self.returnToCase)

    def handleIfBody(self, block, ifCaseString):
        ifcase = getattr(block, ifCaseString)
        if ifCaseString == 'iffalse' and ifcase is None:
            return None
        jumpToCase = self.currentCaseNumber
        if isinstance(ifcase, c_ast.Compound):
            self.createCasesForIfBody(ifcase)
            returnToCase = jumpToCase if ifCaseString == 'iffalse' else self.caseNumber + 1
            trueCase = c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep", None),
                                                        c_ast.Constant("int", str(returnToCase), None),
                                                        None)])
        elif isinstance(ifcase, c_ast.If):
            trueCase = c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep", None),
                                                        c_ast.Constant("int", str(self.currentCaseNumber), None),
                                                        None)])
            flattenPart = FlattenPart(ifcase, self.currentCaseNumber,
                                      self.returnToCase)  # Note only happens in false case of if
            self.cases.extend(flattenPart.getCases())
            self.currentCaseNumber = flattenPart.getCurrentCaseNumber()

        else:
            self.callsFunctionNotInFile = (
                    ifCaseString == 'iftrue' and not isinstance(ifcase, c_ast.Return))
            trueCase = c_ast.Compound([ifcase], None)
        return trueCase


class FlattenLoop:
    def __init__(self, ast):
        self.isWhile = 0
        self.newBlockItems = [
            c_ast.Decl("run", None, None, None, None,
                       c_ast.TypeDecl("run", None, None, c_ast.IdentifierType(['bool'], None), None),
                       c_ast.Constant("int", "1", None), None, None, ),
            c_ast.Decl("programStep", None, None, None, None,
                       c_ast.TypeDecl("programStep", None, None, c_ast.IdentifierType(["int"], None), None),
                       c_ast.Constant("int", "1", None), None, None)
        ]

        ast = self.appendDeclerations(ast)
        self.caseCount = 1
        self.switchBody = []
        self.case = []

        self.createSwitchBody(ast)
        self.createLastCaseOfSwitchBody()

        switchBodyCompound = c_ast.Compound(self.switchBody, None)
        switch = [c_ast.Switch(c_ast.ID("programStep", None), switchBodyCompound, None)]

        body = c_ast.Compound(switch, None)
        self.newBlockItems.append(c_ast.While(c_ast.ID("run", None), body, None))

    def createSwitchBody(self, ast):
        for block in ast:
            flattenPart = FlattenPart(block, self.caseCount, 0)
            self.switchBody.extend(flattenPart.getCases())
            self.caseCount = flattenPart.getCurrentCaseNumber()
        self.sortSwitchBody()

    def createLastCaseOfSwitchBody(self):
        case = [c_ast.Assignment("=", c_ast.ID("run", None), c_ast.Constant("int", "0", None), None),
                c_ast.Break(None)]
        self.switchBody.append(c_ast.Case(c_ast.Constant("int", str(self.caseCount), None), case, None))

    def getFlattentLoop(self):
        return self.newBlockItems

    def appendDeclerations(self, ast):
        for count, block in enumerate(ast.block_items):
            if c_ast.Decl != type(block):
                return ast.block_items[count:]
            self.newBlockItems.append(block)

    def sortSwitchBody(self):
        self.switchBody.sort(key=lambda x: int(x.expr.value))


def flattenFunction(func):
    flattenLoops = FlattenLoop(func.body)
    newBody = c_ast.Compound(flattenLoops.getFlattentLoop(), func.body.coord)
    return c_ast.FuncDef(func.decl, func.param_decls, newBody, func.coord)


def flattenLoopsForAllFunction(ast):
    return c_ast.FileAST([flattenFunction(func) for func in ast.ext], ast.coord)
