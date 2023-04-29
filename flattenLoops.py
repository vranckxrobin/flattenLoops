import sys

from pycparser import c_ast
import copy

sys.path.extend(['.', '..'])


class FlattenPart:
    def __init__(self, block, currentCaseNumber, returnToCase):
        self.currentCaseNumber = currentCaseNumber
        self.returnToCase = returnToCase  # TODO Note if zero no returnStatement
        self.cases = []  # cases need to represent the flattent part
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
            returnToCase = returnToWhile if pos == lengthBlock_items else 0  # state to which case to return to 0 is go to next case
            flattenPart = FlattenPart(tempBlock, self.currentCaseNumber,
                                      returnToCase)  # actual flattening of part of the while loop
            self.cases.extend(flattenPart.getCases())  # adding cases to the new functions switch body
            # setting the case number to the old case number + the cases created in the flattening of part of the while loops body
            self.currentCaseNumber = flattenPart.getCurrentCaseNumber()

    def transformWhileConditionToIf(self, block, caseNumber, returnToCase, nextInstruction):
        falseCase = [c_ast.Assignment("=", c_ast.ID("programStep"),
                                      c_ast.Constant("int", str(returnToCase)))]

        case = [c_ast.If(block.cond, c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep"),
                                                                      c_ast.Constant("int", str(nextInstruction)))]),
                         c_ast.Compound(falseCase)),
                c_ast.Break()]
        self.cases.append(
            c_ast.Case(c_ast.Constant("int", str(caseNumber)), case))

    def handleWhileCase(self, block):
        self.currentCaseNumber = self.currentCaseNumber + 1  # add case because first case is the while's if statement
        nextInstruction = self.currentCaseNumber
        self.transformWhileBodyToCases(block, self.caseNumber)
        returnToCase = self.returnToCase if self.returnToCase != 0 else self.currentCaseNumber  # state to which case to return to
        self.transformWhileConditionToIf(block, self.caseNumber, returnToCase, nextInstruction)

    def handleDoWhileCase(self, block):
        nextInstruction = self.currentCaseNumber
        self.transformWhileBodyToCases(block, 0)
        returnToCase = self.returnToCase if self.returnToCase != 0 else self.currentCaseNumber + 1  # state to which case to return to
        self.transformWhileConditionToIf(block, self.currentCaseNumber, returnToCase, nextInstruction)
        self.currentCaseNumber = self.currentCaseNumber + 1  # add case because last case is the while's if statement

    # flatten if statements and calls this class when part of the if statement cases should be flattent
    def handleIfCase(self, block):
        saveSelf = copy.deepcopy(self)  # save state

        returnToCase = self.returnToCase

        # if the condition of if is false we need to jump over the true case statements
        # this if statement is used to get this case number so we know where to jump to
        # not necessary when there is a return statement because this would then be where the
        # else case should point to
        if returnToCase == 0:
            self.currentCaseNumber += 1
            self.handleIfBody(block, 'iftrue')
            self.handleIfBody(block, 'iffalse')
            returnToCase = self.returnToCase if self.returnToCase != 0 else self.currentCaseNumber

            # reset previous save state except fo the returnToCase
            self.currentCaseNumber = saveSelf.currentCaseNumber
            self.cases = saveSelf.cases
            self.returnToCase = saveSelf.returnToCase
            self.caseNumber = saveSelf.caseNumber
            self.returnToCase = returnToCase

        self.callsFunctionNotInFile = False  # Used to add the programSteps in the else case and remove the redunt ones under the if else statement.
        self.currentCaseNumber += 1  # adds 1 for the if statement case it self
        trueCase = self.handleIfBody(block, 'iftrue')  # flattens true case
        self.returnToCase = saveSelf.returnToCase  # restet saved return case
        falseCase = self.handleIfBody(block, 'iffalse')  # flattens false case

        # add programStep in the else case if the else is empty
        if falseCase is None and not self.callsFunctionNotInFile:
            falseCase = c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep"),
                                                         c_ast.Constant("int", str(returnToCase)))])

        case = [c_ast.If(block.cond, trueCase, falseCase)]
        if self.callsFunctionNotInFile:
            case.append(c_ast.Assignment("=", c_ast.ID("programStep"),
                                         c_ast.Constant("int",
                                                        str(returnToCase))))  # point to what is outside the if statement (returnToCase)
        case.append(c_ast.Break())
        self.cases.append(
            c_ast.Case(c_ast.Constant("int", str(self.caseNumber)), case))  # programstep of this case (self.caseNumber)

    # For cases that don't need to be flattent
    # Create a case with the block inside
    def handleDefault(self, block):
        self.currentCaseNumber += 1
        returnToCase = (
            self.returnToCase if self.returnToCase != 0 else self.currentCaseNumber
        )
        temp = [block, c_ast.Assignment(
            "=",
            c_ast.ID("programStep"),
            c_ast.Constant("int", str(returnToCase))
        ), c_ast.Break()]
        self.cases.append(
            c_ast.Case(c_ast.Constant("int", str(self.caseNumber)), temp))

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

    # determinses wich cases need to be flattent
    def needsFlattening(self, param):
        return param in [c_ast.While, c_ast.If, c_ast.DoWhile]

    # creates a case that bundles all statements provided in the operations parameter
    # and let the case jump to the correct case with the returnToCase
    # when the returnToCase is 0 jump to the next case
    def createCase(self, operations, returnToCase):
        tmpCaseNumber = self.currentCaseNumber
        self.currentCaseNumber += 1
        returnToCase = returnToCase if returnToCase != 0 else self.currentCaseNumber
        operations.append(c_ast.Assignment("=", c_ast.ID("programStep"),
                                           c_ast.Constant("int", str(returnToCase))))
        operations.append(c_ast.Break())
        self.cases.append(
            c_ast.Case(c_ast.Constant("int", str(tmpCaseNumber)), operations))

    # Creates cases when the if case is of c_ast.Compound type
    def createCasesForIfBody(self, ifcase):
        creatingCase = False  # used for bundeling statements that don't need to be flattent
        temp = []
        lengthBlock_items = len(ifcase.block_items.block_items) - 1
        for pos, tempBlock in enumerate(ifcase.block_items.block_items):
            if self.needsFlattening(type(tempBlock)):  # checks if the current statement needs to be flattent
                if creatingCase: #if there was a case being made first create it
                    creatingCase = False
                    self.createCase(temp, 0)
                    temp = []
                #flatten the current statement
                returnToCase = self.returnToCase if pos == lengthBlock_items else 0
                flattenPart = FlattenPart(tempBlock, self.currentCaseNumber,
                                          returnToCase)
                self.cases.extend(flattenPart.getCases()) #add the flattent case to this cases
                # setting the case number to the old case number + the cases created in the flattening of part of the while loops body
                self.currentCaseNumber = flattenPart.getCurrentCaseNumber() #updat
            else:
                creatingCase = True
                temp.append(tempBlock)
        if creatingCase: #if there was a case being made create it
            self.createCase(temp, self.returnToCase)

    #create cases for if statements case (true case or false case)
    def handleIfBody(self, block, ifCaseString):
        ifcase = getattr(block, ifCaseString)
        if ifCaseString == 'iffalse' and ifcase is None:
            return None
        jumpToCase = self.currentCaseNumber
        if isinstance(ifcase, c_ast.Compound):
            self.createCasesForIfBody(ifcase)
            returnToCase = jumpToCase if ifCaseString == 'iffalse' else self.caseNumber + 1
            trueCase = c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep"),
                                                        c_ast.Constant("int", str(returnToCase)))])
        elif isinstance(ifcase, c_ast.If):
            trueCase = c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep"),
                                                        c_ast.Constant("int", str(self.currentCaseNumber)))])
            flattenPart = FlattenPart(ifcase, self.currentCaseNumber,
                                      self.returnToCase)  # Note only happens in false case of if
            self.cases.extend(flattenPart.getCases())
            self.currentCaseNumber = flattenPart.getCurrentCaseNumber()

        else:
            self.callsFunctionNotInFile = (
                    ifCaseString == 'iftrue' and not isinstance(ifcase, c_ast.Return))
            trueCase = c_ast.Compound([ifcase])
        return trueCase


class FlattenFunc:
    def __init__(self, ast):
        # adds 2 variables to control the flow of the program
        self.newBlockItems = [
            c_ast.Decl("run", None, None, None, None,
                       c_ast.TypeDecl("run", None, None, c_ast.IdentifierType(['bool'])),
                       c_ast.Constant("int", "1"), None),
            c_ast.Decl("programStep", None, None, None, None,
                       c_ast.TypeDecl("programStep", None, None, c_ast.IdentifierType(["int"])),
                       c_ast.Constant("int", "1"), None)
        ]

        ast = self.appendDeclerations(ast)
        self.caseCount = 1
        self.switchBody = []

        self.createSwitchBody(ast)  # create the cases for the switch
        self.createLastCaseOfSwitchBody()

        # create the switch statement
        switch = [c_ast.Switch(c_ast.ID("programStep"), c_ast.Compound(self.switchBody))]

        # create the while loop
        self.newBlockItems.append(c_ast.While(c_ast.ID("run"), c_ast.Compound(switch)))

    # create cases for the switchbody
    def createSwitchBody(self, ast):
        for block in ast:
            flattenPart = FlattenPart(block, self.caseCount, 0)
            self.switchBody.extend(flattenPart.getCases())
            self.caseCount = flattenPart.getCurrentCaseNumber()
        self.sortSwitchBody()

    # create the last case for the switchbody the termination of the loop
    def createLastCaseOfSwitchBody(self):
        case = [c_ast.Assignment("=", c_ast.ID("run"), c_ast.Constant("int", "0")),
                c_ast.Break()]
        self.switchBody.append(c_ast.Case(c_ast.Constant("int", str(self.caseCount)), case))

    def getFlattentLoop(self):
        return self.newBlockItems

    # adds the declerations to the newBlockItems variable (which will be the new function)
    def appendDeclerations(self, ast):
        for count, block in enumerate(ast.block_items):
            if c_ast.Decl != type(block):
                return ast.block_items[count:]
            self.newBlockItems.append(block)

    # sort switch according to programStep
    def sortSwitchBody(self):
        self.switchBody.sort(key=lambda x: int(x.expr.value))

#flattens a function
def flattenFunction(func):
    flattenFunc = FlattenFunc(func.body)
    newBody = c_ast.Compound(flattenFunc.getFlattentLoop())
    return c_ast.FuncDef(func.decl, func.param_decls, newBody)

#flattens all the functions
def flattenLoopsForAllFunction(ast):
    return c_ast.FileAST([flattenFunction(func) for func in ast.ext])
