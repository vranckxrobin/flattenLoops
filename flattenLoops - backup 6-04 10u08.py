import sys

from pycparser import c_ast

sys.path.extend(['.', '..'])

#TODO don't flatten functions without loops



class FlattenPart:
    def __init__(self, block, currentCaseNumber, returnToCase,ofset=0):
        self.currentCaseNumber = currentCaseNumber
        self.returnToCase = returnToCase  # TODO Note if zero no returnStatement
        self.cases = []
        self.caseNumber = currentCaseNumber
        self.ofset=ofset

        self.flattenCaseByType(block)

    def getCurrentCaseNumber(self):
        return self.currentCaseNumber

    def getCases(self):
        return self.cases

    def flattenCaseByType(self, block):
        coord1 = None  # Todo bit further then below example smallLoopTest.c:4:5
        coord = None  # TODO proper Coord example smallLoopTest.c:4:10 (column 10, file smallLoopTest.c, line 4)
        coord2 = None  # TODO should be a bit further example is smallLoopTest.c:4:16

        match type(block):  # TODO add switch
            case c_ast.While:  # TODO createDoWhile and if
                case = []
                # TODO if brackets not on corect indent and is this even a problem?
                case.append(c_ast.If(block.cond, c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep", coord1),
                                                                                  c_ast.Constant("int",
                                                                                                 str(self.currentCaseNumber + 1),
                                                                                                 coord2), coord)]),
                                     None, coord))  # point to what is inside the loop (tmpCaseCount+ 1)

                self.currentCaseNumber = self.currentCaseNumber + 1
                pos = -1
                lengthBlock_items = len(block.stmt.block_items) - 1
                for tempBlock in block.stmt.block_items:
                    pos += 1
                    if pos == lengthBlock_items:
                        returnToCase = self.caseNumber
                    else:
                        returnToCase = 0
                    flattenPart = FlattenPart(tempBlock, self.currentCaseNumber, returnToCase)
                    self.cases.extend(flattenPart.getCases())
                    self.currentCaseNumber = flattenPart.getCurrentCaseNumber()
                self.currentCaseNumber+=self.ofset# self.ofset aded 1 instead of this because it looks like this is needed TODO check if correct put this into if because in parseatt always added 1 to case number only needed for first one
                # because otherwise it doesn't jump far enough TODO check if correct in every case now it seems correct

                if self.returnToCase != 0:
                    returnToCase = self.returnToCase
                else:
                    returnToCase = self.currentCaseNumber

                case.append(c_ast.Assignment("=", c_ast.ID("programStep", coord1),
                                             c_ast.Constant("int", str(returnToCase), coord2),
                                             coord))  # point to what is outside the loop (tmpCaseCount+ 2)
                case.append(c_ast.Break(coord))
                self.cases.append(
                    c_ast.Case(c_ast.Constant("int", str(self.caseNumber), coord1), case,
                               coord))  # programstep of this case (tmpCaseCount)
            case c_ast.If:
                case = []
                trueCase=self.handleTrueCaseOfIf(block)
                falseCase = self.handleFalseCaseOfIf(block)
                #trueCase=self.handleLastTrueCase(trueCase) #TODO
                if self.returnToCase != 0:
                    returnToCase = self.returnToCase
                else:
                    returnToCase = self.currentCaseNumber
                case.append(c_ast.If(block.cond, trueCase, falseCase, coord))
                case.append(c_ast.Assignment("=", c_ast.ID("programStep", coord1),
                                             c_ast.Constant("int", str(returnToCase), coord2),
                                             # TODO maybe tmpCaseCount needs to be replase by self.caseCount
                                             coord))  # point to what is outside the loop (tmpCaseCount+ 2)
                case.append(c_ast.Break(coord))
                self.cases.append(
                    c_ast.Case(c_ast.Constant("int", str(self.caseNumber), coord1), case,
                               coord))  # programstep of this case (tmpCaseCount)

            case _:  # TODO create case while not while type or if type just add to case and return it
                self.currentCaseNumber += 1
                temp = []
                temp.append(block)
                if self.returnToCase != 0:
                    returnToCase = self.returnToCase
                else:
                    returnToCase = self.currentCaseNumber
                temp.append(c_ast.Assignment("=", c_ast.ID("programStep", coord1),
                                             c_ast.Constant("int", str(returnToCase), coord2),
                                             coord))
                self.cases.append(
                    c_ast.Case(c_ast.Constant("int", str(self.caseNumber), coord1), temp,
                               coord))

    def needsFlattening(self, param):
        return (param == c_ast.While) or (param == c_ast.If) #TODO delete  or (param == c_ast.UnaryOp) test Debug

    #TODO TrueCase and FalseCase can be combined
    #TODO optimize if condition creates the iftrue with and else to the nex if combine this into 1 statement and remove the lower programstep = 1 if last one is else
    def handleTrueCaseOfIf(self, block):
        coord1 = None  # Todo bit further then below example smallLoopTest.c:4:5
        coord = None  # TODO proper Coord example smallLoopTest.c:4:10 (column 10, file smallLoopTest.c, line 4)
        coord2 = None  # TODO should be a bit further example is smallLoopTest.c:4:16
        if c_ast.Compound == type(block.iftrue):
            self.currentCaseNumber += 1
            creatingCase = False
            temp = []
            pos = -1
            lengthBlock_items = len(block.iftrue.block_items.block_items) - 1
            for tempBlock in block.iftrue.block_items.block_items:
                pos += 1
                if self.needsFlattening(type(tempBlock)):
                    if creatingCase:
                        creatingCase = False
                        tmpCaseNumber = self.currentCaseNumber
                        self.currentCaseNumber += 1
                        temp.append(c_ast.Assignment("=", c_ast.ID("programStep", coord1),
                                                     c_ast.Constant("int", str(self.currentCaseNumber), coord2),
                                                     coord))
                        self.cases.append(
                            c_ast.Case(c_ast.Constant("int", str(tmpCaseNumber), coord1), temp,
                                       coord))
                        temp = []
                    if pos == lengthBlock_items:
                        returnToCase = self.returnToCase
                    else:
                        returnToCase = 0
                    flattenPart = FlattenPart(tempBlock, self.currentCaseNumber,
                                              returnToCase)  # TODO implement return
                    self.cases.extend(flattenPart.getCases())
                    self.currentCaseNumber = flattenPart.getCurrentCaseNumber()
                else:
                    creatingCase = True
                    temp.append(tempBlock)
            if creatingCase:
                tmpCaseNumber = self.currentCaseNumber
                if self.returnToCase != 0:
                    returnToCase = self.returnToCase
                else:
                    returnToCase = self.currentCaseNumber
                temp.append(c_ast.Assignment("=", c_ast.ID("programStep", coord1),
                                             c_ast.Constant("int", str(returnToCase), coord2),
                                             coord))
                self.cases.append(
                    c_ast.Case(c_ast.Constant("int", str(tmpCaseNumber), coord1), temp,
                               coord))

            returnToCase = self.caseNumber + 1
            trueCase = c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep", coord1),
                                                        c_ast.Constant("int", str(returnToCase), coord2),
                                                        coord)])
        elif c_ast.If == type(block.iftrue):
            self.currentCaseNumber += 1 #TODO check but should work same as ifFalse
            tmpCaseNumber = self.currentCaseNumber
            flattenPart = FlattenPart(block.iffalse, self.currentCaseNumber, self.returnToCase)
            self.cases.extend(flattenPart.getCases())
            self.currentCaseNumber = flattenPart.getCurrentCaseNumber()
            trueCase = c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep", coord1),
                                                        c_ast.Constant("int", str(tmpCaseNumber), coord2),
                                                        coord)])
            if False:
                self.currentCaseNumber += 1
                trueCase = c_ast.Compound([block.iftrue])  # TODO implement placeHolder
                trueCase.coord = None
        else:
            self.currentCaseNumber += 1  # NOTE is commented out because it doesn't create a case for example just return can be copied over
            trueCase = c_ast.Compound([block.iftrue])
            trueCase.coord = None
        return trueCase

    def handleFalseCaseOfIf(self, block):
        if block.iffalse is None:
            return None
        coord1 = None  # Todo bit further then below example smallLoopTest.c:4:5
        coord = None  # TODO proper Coord example smallLoopTest.c:4:10 (column 10, file smallLoopTest.c, line 4)
        coord2 = None  # TODO should be a bit further example is smallLoopTest.c:4:16
        if c_ast.Compound == type(block.iffalse):
            if block.iffalse.coord.line==130:#TODO delete this is Debug
                pass
            self.currentCaseNumber += 1
            creatingCase = False
            temp = []
            pos = -1
            lengthBlock_items = len(block.iffalse.block_items.block_items) - 1
            for tempBlock in block.iffalse.block_items.block_items:
                pos += 1
                if self.needsFlattening(type(tempBlock)):
                    if creatingCase:
                        creatingCase = False
                        tmpCaseNumber = self.currentCaseNumber
                        self.currentCaseNumber += 1
                        if self.currentCaseNumber== 5 or self.currentCaseNumber==27:#TODO DElete this is Debug
                            pass
                        temp.append(c_ast.Assignment("=", c_ast.ID("programStep", coord1),
                                                     c_ast.Constant("int", str(self.currentCaseNumber), coord2),
                                                     coord))
                        self.cases.append(
                            c_ast.Case(c_ast.Constant("int", str(tmpCaseNumber), coord1), temp,
                                       coord))
                        temp = []
                    if pos == lengthBlock_items:
                        returnToCase = self.returnToCase
                    else:
                        returnToCase = 0
                    flattenPart = FlattenPart(tempBlock, self.currentCaseNumber,
                                              returnToCase)  # TODO implement return
                    self.cases.extend(flattenPart.getCases())
                    self.currentCaseNumber = flattenPart.getCurrentCaseNumber()
                else:
                    creatingCase = True
                    temp.append(tempBlock)
            if creatingCase:
                tmpCaseNumber = self.currentCaseNumber
                if self.returnToCase != 0:
                    returnToCase = self.returnToCase
                else:
                    returnToCase = self.currentCaseNumber
                    if returnToCase == 5 or returnToCase==27:  # TODO DElete this is Debug
                        pass
                temp.append(c_ast.Assignment("=", c_ast.ID("programStep", coord1),
                                             c_ast.Constant("int", str(returnToCase), coord2),
                                             coord))
                self.cases.append(
                    c_ast.Case(c_ast.Constant("int", str(tmpCaseNumber), coord1), temp,
                               coord))

            returnToCase = self.currentCaseNumber #TODO replace from self.caseNumber + 1 because this caused steps to point to the same as in the if case (this is the else case)
            if returnToCase == 5 or returnToCase==27:  # TODO DElete this is Debug
                pass
            trueCase = c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep", coord1),
                                                        c_ast.Constant("int", str(returnToCase), coord2),
                                                        coord)])
        elif c_ast.If == type(block.iffalse):
            self.currentCaseNumber += 1
            tmpCaseNumber = self.currentCaseNumber
            flattenPart = FlattenPart(block.iffalse, self.currentCaseNumber, self.returnToCase)
            self.cases.extend(flattenPart.getCases())
            self.currentCaseNumber = flattenPart.getCurrentCaseNumber()
            if tmpCaseNumber == 5 or tmpCaseNumber==27:  # TODO DElete this is Debug
                pass
            trueCase = c_ast.Compound([c_ast.Assignment("=", c_ast.ID("programStep", coord1),
                                                        c_ast.Constant("int", str(tmpCaseNumber), coord2),
                                                        coord)])
            if False:
                self.currentCaseNumber += 1
                trueCase = c_ast.Compound([block.iffalse])  # TODO implement placeHolder
                trueCase.coord = None
        else:
            self.currentCaseNumber += 1  # NOTE is commented out because it doesn't create a case for example just return can be copied over
            trueCase = c_ast.Compound([block.iffalse])
            trueCase.coord = None
        return trueCase


class FlattenLoop:
    def __init__(self, ast):
        self.isWhile = 0
        # TODO maybe coord not necessary
        self.newBlockItems = []
        coord1 = None  # Todo bit further then below example smallLoopTest.c:4:5
        coord = None  # TODO proper Coord example smallLoopTest.c:4:10 (column 10, file smallLoopTest.c, line 4)
        coord2 = None  # TODO should be a bit further example is smallLoopTest.c:4:16
        self.newBlockItems.append(c_ast.Decl("run", None, None, None, None,
                                             c_ast.TypeDecl("run", None, None, c_ast.IdentifierType(['bool'], coord1),
                                                            coord), c_ast.Constant("int", "1", coord2), None, coord))
        # TODO set coord, coord1 en coord2
        self.newBlockItems.append(c_ast.Decl("programStep", None, None, None, None,
                                             c_ast.TypeDecl("programStep", None, None,
                                                            c_ast.IdentifierType(["int"], coord1),
                                                            coord), c_ast.Constant("int", "1", coord2), None, coord))

        ast = self.appendDeclerations(ast)
        self.caseCount = 1
        # TODO coord
        self.switchBody = []
        self.createSwitchBody(ast)
        self.createLastCaseOfSwitchBody()

        switchBodyCompound = c_ast.Compound(self.switchBody, coord)
        switch = [c_ast.Switch(c_ast.ID("programStep", coord), switchBodyCompound, coord)]

        # TODO coord
        body = c_ast.Compound(switch, coord)
        # TODO coord
        self.newBlockItems.append(c_ast.While(c_ast.ID("run", coord1), body, coord))
        # TODO something like this self.newBlockItems.append(self.remaining)

    def closeCaseIfOpen(self):
        coord1 = None  # Todo bit further then below example smallLoopTest.c:4:5
        coord = None  # TODO proper Coord example smallLoopTest.c:4:10 (column 10, file smallLoopTest.c, line 4)
        coord2 = None  # TODO should be a bit further example is smallLoopTest.c:4:16
        if self.case != []:
            self.case.append(c_ast.Assignment("=", c_ast.ID("programStep", coord1),
                                              c_ast.Constant("int", str(self.caseCount + 1), coord2),
                                              coord))  # point to what is outside the loop (tmpCaseCount+ 2)
            self.case.append(c_ast.Break(coord))
            self.switchBody.append(
                c_ast.Case(c_ast.Constant("int", str(self.caseCount), coord1), self.case, coord))
            self.caseCount += 1
            self.case = []

    def createSwitchBody(self, ast):
        coord1 = None  # Todo bit further then below example smallLoopTest.c:4:5
        coord = None  # TODO proper Coord example smallLoopTest.c:4:10 (column 10, file smallLoopTest.c, line 4)
        coord2 = None  # TODO should be a bit further example is smallLoopTest.c:4:16
        self.caseCount = 1
        self.case = []
        for block in ast:
            flattenPart = FlattenPart(block, self.caseCount, 0,1)
            self.switchBody.extend(flattenPart.getCases())
            self.caseCount = flattenPart.getCurrentCaseNumber()
        self.sortSwitchBody()

    def createLastCaseOfSwitchBody(self):
        coord1 = None  # Todo bit further then below example smallLoopTest.c:4:5
        coord = None  # TODO proper Coord example smallLoopTest.c:4:10 (column 10, file smallLoopTest.c, line 4)
        coord2 = None  # TODO should be a bit further example is smallLoopTest.c:4:16
        case = [c_ast.Assignment("=", c_ast.ID("run", coord1), c_ast.Constant("int", "0", coord2), coord),
                c_ast.Break(coord)]
        self.switchBody.append(c_ast.Case(c_ast.Constant("int", str(self.caseCount), coord1), case, coord))

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



