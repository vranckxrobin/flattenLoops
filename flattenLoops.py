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
        pos = -1
        lengthBlock_items = len(block.stmt.block_items) - 1
        for tempBlock in block.stmt.block_items:
            pos += 1
            if pos == lengthBlock_items:
                returnToCase = returnToWhile
            else:
                returnToCase = 0
            flattenPart = FlattenPart(tempBlock, self.currentCaseNumber, returnToCase)
            self.cases.extend(flattenPart.getCases())
            self.currentCaseNumber = flattenPart.getCurrentCaseNumber()

    def transformWhileConditionToIf(self, block, caseNumber, returnToCase, nextInstruction):
        case = []

        falseCase = [c_ast.Assignment("=", c_ast.ID("programStep", None),
                                      c_ast.Constant("int", str(returnToCase), None),
                                      None)]

        case.append(c_ast.If(block.cond, c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep", None),
                                                                          c_ast.Constant("int",
                                                                                         str(nextInstruction),
                                                                                         None), None)]),
                             c_ast.Compound(falseCase),
                             None))  # point to what is inside the loop (tmpCaseCount+ 1)
        case.append(c_ast.Break(None))

        self.cases.append(
            c_ast.Case(c_ast.Constant("int", str(caseNumber), None), case,
                       None))  # programstep of this case (tmpCaseCount)

    def handleWhileCase(self, block):

        # TODO if brackets not on corect indent and is this even a problem?
        self.currentCaseNumber = self.currentCaseNumber + 1
        nextInstruction = self.currentCaseNumber
        self.transformWhileBodyToCases(block, self.caseNumber)
        if self.returnToCase != 0:
            returnToCase = self.returnToCase
        else:
            returnToCase = self.currentCaseNumber
        self.transformWhileConditionToIf(block, self.caseNumber, returnToCase, nextInstruction)

    def handleDoWhileCase(self, block):
        nextInstruction = self.currentCaseNumber
        self.transformWhileBodyToCases(block, 0)
        if self.returnToCase != 0:
            returnToCase = self.returnToCase
        else:
            returnToCase = self.currentCaseNumber + 1
        self.transformWhileConditionToIf(block, self.currentCaseNumber, returnToCase, nextInstruction)
        self.currentCaseNumber = self.currentCaseNumber + 1

    def handleIfCase(self, block):
        case = []
        saveSelf = copy.deepcopy(self)
        # self.handleTrueCaseOfIf(block)
        # self.handleFalseCaseOfIf(block)
        self.currentCaseNumber += 1
        self.handleIfBody(block, 'iftrue')
        self.handleIfBody(block, 'iffalse')

        if self.returnToCase != 0:
            returnToCase = self.returnToCase
        else:
            returnToCase = self.currentCaseNumber

        # TODO reset self do truecase and false case aagain but now for the truecase with the returning of the if function
        self.currentCaseNumber = saveSelf.currentCaseNumber
        self.cases = saveSelf.cases
        self.returnToCase = saveSelf.returnToCase
        self.caseNumber = saveSelf.caseNumber
        # self.ofset = saveSelf.ofset

        self.returnToCase = returnToCase
        self.callsFunctionNotInFile = False
        # trueCase = self.handleTrueCaseOfIf(block)
        self.currentCaseNumber += 1
        trueCase = self.handleIfBody(block, 'iftrue')
        self.returnToCase = saveSelf.returnToCase
        # falseCase = self.handleFalseCaseOfIf(block)
        falseCase = self.handleIfBody(block, 'iffalse')

        if falseCase is None and not self.callsFunctionNotInFile:
            falseCase = c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep", None),
                                                         c_ast.Constant("int", str(returnToCase), None),
                                                         None)])  # point to what is outside the loop (returnToCase)

        case.append(c_ast.If(block.cond, trueCase, falseCase, None))
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
        temp = []
        temp.append(block)
        if self.returnToCase != 0:
            returnToCase = self.returnToCase
        else:
            returnToCase = self.currentCaseNumber
        temp.append(c_ast.Assignment("=", c_ast.ID("programStep", None),
                                     c_ast.Constant("int", str(returnToCase), None),
                                     None))
        temp.append(c_ast.Break(None))
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
        return (param == c_ast.While) or (param == c_ast.If) or (
                param == c_ast.DoWhile)

    def handleIfBody(self, block, ifCaseString):
        if ifCaseString == 'iffalse' and getattr(block, ifCaseString) is None:
            return None
        jumpToCase = self.currentCaseNumber
        if c_ast.Compound == type(getattr(block, ifCaseString)):
            creatingCase = False
            temp = []
            pos = -1
            lengthBlock_items = len(getattr(block, ifCaseString).block_items.block_items) - 1
            for tempBlock in getattr(block, ifCaseString).block_items.block_items:
                pos += 1
                if self.needsFlattening(type(tempBlock)):
                    if creatingCase:
                        creatingCase = False
                        tmpCaseNumber = self.currentCaseNumber
                        self.currentCaseNumber += 1
                        temp.append(c_ast.Assignment("=", c_ast.ID("programStep", None),
                                                     c_ast.Constant("int", str(self.currentCaseNumber), None),
                                                     None))
                        temp.append(c_ast.Break(None))
                        self.cases.append(
                            c_ast.Case(c_ast.Constant("int", str(tmpCaseNumber), None), temp,
                                       None))
                        temp = []
                    if pos == lengthBlock_items:
                        returnToCase = self.returnToCase
                    else:
                        returnToCase = 0
                    flattenPart = FlattenPart(tempBlock, self.currentCaseNumber,
                                              returnToCase)
                    self.cases.extend(flattenPart.getCases())
                    self.currentCaseNumber = flattenPart.getCurrentCaseNumber()
                else:
                    creatingCase = True
                    temp.append(tempBlock)
            if creatingCase:
                tmpCaseNumber = self.currentCaseNumber
                self.currentCaseNumber += 1
                if self.returnToCase != 0:
                    returnToCase = self.returnToCase
                else:
                    returnToCase = self.currentCaseNumber
                temp.append(c_ast.Assignment("=", c_ast.ID("programStep", None),
                                             c_ast.Constant("int", str(returnToCase), None),
                                             None))
                temp.append(c_ast.Break(None))
                self.cases.append(
                    c_ast.Case(c_ast.Constant("int", str(tmpCaseNumber), None), temp,
                               None))
            if ifCaseString == 'iffalse':
                returnToCase = jumpToCase
            else:
                returnToCase = self.caseNumber + 1
            trueCase = c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep", None),
                                                        c_ast.Constant("int", str(returnToCase), None),
                                                        None)])
        elif c_ast.If == type(getattr(block, ifCaseString)):
            tmpCaseNumber = self.currentCaseNumber
            flattenPart = FlattenPart(getattr(block, ifCaseString), self.currentCaseNumber,
                                      self.returnToCase)  # Note only happens in false case of if
            self.cases.extend(flattenPart.getCases())
            self.currentCaseNumber = flattenPart.getCurrentCaseNumber()
            trueCase = c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep", None),
                                                        c_ast.Constant("int", str(tmpCaseNumber), None),
                                                        None)])
        else:
            if ifCaseString == 'iftrue' and type(
                    getattr(block, ifCaseString)) != c_ast.Return:  # Note only happens for true case
                self.callsFunctionNotInFile = True
            trueCase = c_ast.Compound([getattr(block, ifCaseString)])
            trueCase.coord = None
        return trueCase


class FlattenLoop:
    def __init__(self, ast):
        self.isWhile = 0
        self.newBlockItems = []
        self.newBlockItems.append(c_ast.Decl("run", None, None, None, None,
                                             c_ast.TypeDecl("run", None, None, c_ast.IdentifierType(['bool'], None),
                                                            None), c_ast.Constant("int", "1", None), None,
                                             None))  # TODO gives problem if run and programstep is defined should check to replace
        self.newBlockItems.append(c_ast.Decl("programStep", None, None, None, None,
                                             c_ast.TypeDecl("programStep", None, None,
                                                            c_ast.IdentifierType(["int"], None),
                                                            None), c_ast.Constant("int", "1", None), None, None))

        ast = self.appendDeclerations(ast)
        self.caseCount = 1
        self.switchBody = []
        self.createSwitchBody(ast)
        self.createLastCaseOfSwitchBody()

        switchBodyCompound = c_ast.Compound(self.switchBody, None)
        switch = [c_ast.Switch(c_ast.ID("programStep", None), switchBodyCompound, None)]

        body = c_ast.Compound(switch, None)
        self.newBlockItems.append(c_ast.While(c_ast.ID("run", None), body, None))

    def closeCaseIfOpen(self):
        if self.case != []:
            self.case.append(c_ast.Assignment("=", c_ast.ID("programStep", None),
                                              c_ast.Constant("int", str(self.caseCount + 1), None),
                                              None))  # point to what is outside the loop (tmpCaseCount+ 2)
            self.case.append(c_ast.Break(None))
            self.switchBody.append(
                c_ast.Case(c_ast.Constant("int", str(self.caseCount), None), self.case, None))
            self.caseCount += 1
            self.case = []

    def createSwitchBody(self, ast):
        self.caseCount = 1
        self.case = []
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
        count: int = 0
        for block in ast.block_items:
            if c_ast.Decl == type(block):
                self.newBlockItems.append(block)
                count += 1
            else:
                return ast.block_items[count:]

    def sortSwitchBody(self):
        self.switchBody.sort(key=lambda x: int(x.expr.value))


def flattenLoopsForAllFunction(ast):
    newAst = c_ast.FileAST([], ast.coord)
    for funcDef in ast.ext:
        newBody = c_ast.Compound([], funcDef.body.coord)
        flattenLoops = FlattenLoop(funcDef.body)
        newBody.block_items = flattenLoops.getFlattentLoop()
        newFuncDef = c_ast.FuncDef(funcDef.decl, funcDef.param_decls, newBody, funcDef.coord)
        newAst.ext.append(newFuncDef)
    return newAst
