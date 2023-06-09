import sys
from pycparser import c_ast
import copy

sys.path.extend(['.', '..'])


class FlattenStmt:
    def __init__(self, stmt, currentCaseNumber, returnToCase):
        self.currentCaseNumber = currentCaseNumber
        self.returnToCase = returnToCase  # TODO Note if zero no returnStatement
        self.cases = []  # cases to represent the flattened part
        self.caseNumber = currentCaseNumber
        self.callsFunctionNotInFile = False
        self.flattenCaseByType(stmt)

    def getCurrentCaseNumber(self):
        return self.currentCaseNumber

    def getCases(self):
        return self.cases

    def transformWhileBodyToCases(self, block_items, returnToWhile):
        lengthBlock_items = len(block_items) - 1
        for pos, tempBlock in enumerate(block_items):
            returnToCase = returnToWhile if pos == lengthBlock_items else 0  # state to which case to return to 0 is go to next case
            flattenStmt = FlattenStmt(tempBlock, self.currentCaseNumber,
                                      returnToCase)  # actual flattening of part of the while loop
            self.cases.extend(flattenStmt.getCases())  # add cases to the new functions switch body
            # set the case number to the old case number + the cases created by flattening part of the while loop body
            self.currentCaseNumber = flattenStmt.getCurrentCaseNumber()

    def transformWhileConditionToIf(self, stmt, caseNumber, returnToCase, nextInstruction):
        falseCase= [c_ast.Assignment("=", c_ast.ID("programStep"),
                                                       c_ast.Constant("int",
                                                                      str(returnToCase)))]  # List[Union[c_ast.Assignment,c_ast.Constant]]

        case = [c_ast.If(stmt.cond, c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep"),
                                                                                      c_ast.Constant("int",
                                                                                                     str(nextInstruction)))]),
                                          c_ast.Compound(falseCase)),
                                 c_ast.Break()]
        self.cases.append(
            c_ast.Case(c_ast.Constant("int", str(caseNumber)), case))

    def handleWhileCase(self, stmt):
        self.currentCaseNumber = self.currentCaseNumber + 1  # add case because first case is the while's if statement
        nextInstruction = self.currentCaseNumber
        self.transformWhileBodyToCases(stmt.stmt.block_items, self.caseNumber)
        returnToCase = self.returnToCase if self.returnToCase != 0 else self.currentCaseNumber  # Sets to which case to return to
        self.transformWhileConditionToIf(stmt, self.caseNumber, returnToCase, nextInstruction)

    def handleDoWhileCase(self, stmt):
        nextInstruction = self.currentCaseNumber
        self.transformWhileBodyToCases(stmt.stmt.block_items, 0)
        returnToCase = self.returnToCase if self.returnToCase != 0 else self.currentCaseNumber + 1  # Sets to which case to return to
        self.transformWhileConditionToIf(stmt, self.currentCaseNumber, returnToCase, nextInstruction)
        self.currentCaseNumber = self.currentCaseNumber + 1  # add case because last case is the while's if statement

    def calculateReturnStatementForIf(self, ifStatement):
        if self.returnToCase != 0:
            return self.returnToCase

        saveSelf = copy.deepcopy(self)  # save state

        # if the condition of if is false we need to jump over the true case statements
        # This if statement is used to get that case number so we know where to jump to.
        # Not necessary if there is a return statement, because that would be where the
        # else case should point to
        self.currentCaseNumber += 1
        self.handleIfBody(ifStatement, 'iftrue')
        self.handleIfBody(ifStatement, 'iffalse')
        returnToCase = self.returnToCase if self.returnToCase != 0 else self.currentCaseNumber

        # reset the previous save state except for the returnToCase
        self.currentCaseNumber = saveSelf.currentCaseNumber
        self.cases = saveSelf.cases
        self.returnToCase = saveSelf.returnToCase
        self.caseNumber = saveSelf.caseNumber
        self.returnToCase = returnToCase

        return returnToCase

    # flattens if statements and calls this class when part of the if statement cases should be flattened
    def handleIfCase(self, stmt):
        previousReturnToCase = self.returnToCase
        returnToCase=self.calculateReturnStatementForIf(stmt)

        self.callsFunctionNotInFile = False  # Used to add the programSteps in the else case and remove the redunt ones under the if else statement.
        self.currentCaseNumber += 1  # add 1 for the case of the if statement itself
        trueCase = self.handleIfBody(stmt, 'iftrue')  # flattens true case
        self.returnToCase = previousReturnToCase  # reset saved return case
        falseCase = self.handleIfBody(stmt, 'iffalse')  # flattens false case

        # add programStep in the else case if the else is empty
        if falseCase is None and not self.callsFunctionNotInFile:
            falseCase = c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep"),
                                                         c_ast.Constant("int", str(returnToCase)))])

        case = [c_ast.If(stmt.cond, trueCase, falseCase)]
        if self.callsFunctionNotInFile:
            case.append(c_ast.Assignment("=", c_ast.ID("programStep"),
                                         c_ast.Constant("int",
                                                        str(returnToCase))))  # point to what is outside the if statement (returnToCase)
        case.append(c_ast.Break())
        self.cases.append(
            c_ast.Case(c_ast.Constant("int", str(self.caseNumber)),
                       case))  # program step of this case (self.caseNumber)

    # For cases that don't need to be flattened
    # Create a case with the block inside
    def handleDefault(self, stmt):
        self.currentCaseNumber += 1
        returnToCase = (
            self.returnToCase if self.returnToCase != 0 else self.currentCaseNumber
        )
        temp = [stmt, c_ast.Assignment(
            "=",
            c_ast.ID("programStep"),
            c_ast.Constant("int", str(returnToCase))
        ), c_ast.Break()]
        self.cases.append(
            c_ast.Case(c_ast.Constant("int", str(self.caseNumber)), temp))

    def flattenCaseByType(self, stmt):
        match type(stmt):  # TODO add switch
            case c_ast.While:
                self.handleWhileCase(stmt)
            case c_ast.DoWhile:
                self.handleDoWhileCase(stmt)
            case c_ast.If:
                self.handleIfCase(stmt)
            case _:  #
                self.handleDefault(stmt)

    # Determines which cases need to be flattened.
    def needsFlattening(self, param):
        return param in [c_ast.While, c_ast.If, c_ast.DoWhile]

    # create a case that bundles all the instructions provided in the operations parameter
    # and let the case jump to the correct case with the returnToCase
    # if the returnToCase is 0 jump to the next case
    def createCase(self, operations, returnToCase):
        tmpCaseNumber = self.currentCaseNumber
        self.currentCaseNumber += 1
        returnToCase = returnToCase if returnToCase != 0 else self.currentCaseNumber
        operations.append(c_ast.Assignment("=", c_ast.ID("programStep"),
                                           c_ast.Constant("int", str(returnToCase))))
        operations.append(c_ast.Break())
        self.cases.append(
            c_ast.Case(c_ast.Constant("int", str(tmpCaseNumber)), operations))

    # Creates cases if the if case is of type c_ast.Compound
    def createCasesForIfBody(self, ifcase):
        creatingCase = False  # Used for bundling statements that don't need to be flattened.
        temp = []
        lengthBlock_items = len(ifcase.block_items) - 1
        for pos, tempBlock in enumerate(ifcase.block_items):
            if self.needsFlattening(type(tempBlock)):  # Checks if the current statement needs to be flattened.
                if creatingCase:  # If there was a case that was being made, create it first.
                    creatingCase = False
                    self.createCase(temp, 0)
                    temp = []
                # Flatten the current statement
                returnToCase = self.returnToCase if pos == lengthBlock_items else 0
                flattenStmt = FlattenStmt(tempBlock, self.currentCaseNumber,
                                          returnToCase)
                self.cases.extend(flattenStmt.getCases())  # Add the flattened case to these cases
                # Set the case number to the old case number + the cases created by flattening part of the while loop body.
                self.currentCaseNumber = flattenStmt.getCurrentCaseNumber()
            else:
                creatingCase = True
                temp.append(tempBlock)
        if creatingCase:  # If there was a case being made create it
            self.createCase(temp, self.returnToCase)

    # Create cases for if statements case (true case or false case)
    def handleIfBody(self, stmt, ifCaseString):
        ifcase = getattr(stmt, ifCaseString)
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
            flattenStmt = FlattenStmt(ifcase, self.currentCaseNumber,
                                      self.returnToCase)  # Note that this happens only in the false case of if
            self.cases.extend(flattenStmt.getCases())
            self.currentCaseNumber = flattenStmt.getCurrentCaseNumber()

        else:
            self.callsFunctionNotInFile = (
                    ifCaseString == 'iftrue' and not isinstance(ifcase, c_ast.Return))
            trueCase = c_ast.Compound([ifcase])
        return trueCase


class FlattenFunc:
    def __init__(self, funcBody):
        # Adds 2 variables to the program to control the flow of the program
        self.newBlockItems = [
            c_ast.Decl("run", None, None, None, None,
                       c_ast.TypeDecl("run", None, None, c_ast.IdentifierType(['bool'])),
                       c_ast.Constant("int", "1"), None),
            c_ast.Decl("programStep", None, None, None, None,
                       c_ast.TypeDecl("programStep", None, None, c_ast.IdentifierType(["int"])),
                       c_ast.Constant("int", "1"), None)
        ]

        funcBody = self.appendDeclerations(funcBody)
        self.caseCount = 1
        self.switchBody = []

        self.createSwitchBody(funcBody)  # Create the cases for the switch
        self.createLastCaseOfSwitchBody()

        # Create the switch statement
        switch = [c_ast.Switch(c_ast.ID("programStep"), c_ast.Compound(self.switchBody))]

        # Create the While Loop
        self.newBlockItems.append(c_ast.While(c_ast.ID("run"), c_ast.Compound(switch)))

    # Create cases for the switch body
    def createSwitchBody(self, funcBody):
        for stmt in funcBody:
            flattenStmt = FlattenStmt(stmt, self.caseCount, 0)
            self.switchBody.extend(flattenStmt.getCases())
            self.caseCount = flattenStmt.getCurrentCaseNumber()
        self.sortSwitchBody()

    # Create the last case for the switch body, the termination of the loop.
    def createLastCaseOfSwitchBody(self):
        case = [c_ast.Assignment("=", c_ast.ID("run"), c_ast.Constant("int", "0")),
                c_ast.Break()]
        self.switchBody.append(c_ast.Case(c_ast.Constant("int", str(self.caseCount)), case))

    def getFlattenedLoop(self):
        return self.newBlockItems

    # Adds the declarations to the newBlockItems variable (which will be the new function)
    def appendDeclerations(self, funcBody):
        for count, stmt in enumerate(funcBody.block_items):
            if not isinstance(stmt, c_ast.Decl):
                return funcBody.block_items[count:]
            self.newBlockItems.append(stmt)

    # Sort switch by programStep
    def sortSwitchBody(self):
        self.switchBody.sort(key=lambda x: int(x.expr.value))


# Flattens a function
def flattenFunction(func):
    flattenFunc = FlattenFunc(func.body)
    newBody = c_ast.Compound(flattenFunc.getFlattenedLoop())
    return c_ast.FuncDef(func.decl, func.param_decls, newBody)


# Flattens all the functions
def flattenFile(ast):
    return c_ast.FileAST([flattenFunction(func) for func in ast.ext if isinstance(func, c_ast.FuncDef)])
