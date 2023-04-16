from localVariablesToTopOfFunction import *
from flattenLoops import *
from pycparser import parse_file, c_generator
import re
#TODO tempBlock.stmt.block_items[-1] for last one

class DeclerationsAndAst(object):
    def __init__(self, declerations, func):
        self.declerations = declerations
        self.func = func
        self.currentCase =0
    def getDeclerations(self):
        return self.declerations

    def getFunc(self):
        return self.func

    def setCase(self, currentCase):
        self.currentCase=currentCase

    def getCase(self):
        return self.currentCase


class InlineFunctions:
    def __init__(self,declerations,endOfSwitch,ast,returnToCase,functionVariableName):
        self.oldDeclerations = declerations
        self.newDeclerations=[]
        self.endOfSwitch=endOfSwitch
        self.calls=[]
        self.ast=ast #TODO use this ast instead of passing it around
        self.currentCase=0
        self.first=True
        self.returnToCase=returnToCase
        self.functionVariableName=functionVariableName

    # TODO set the parameterVariable to the one calling this (example bool x= parsealt(p->xml) -> param_p = p->xml;x=parsealt)
    # TODO check if parameter already declared in normal function and rename them(after renaiming check again)
    # TODO check if local variable are already declared and rename them if they have the same name(after renaiming check again)
    def changesDeclaredVariables(self, func, functionName):
        for block in func.body.block_items:
            if type(block)==c_ast.Decl:
                if not self.isInOldDeclerations(block):
                    self.newDeclerations.append(block)

    def isInOldDeclerations(self,block): #TODO change Variables with the same name
        for decl in self.oldDeclerations:
            if decl.name == block.name:
                return True
        return False

    # TODO replace return satement by setting a variable of the type of the return statement and use this variable for returning
    # TODO this return stement should be replaced by setting variable and jumping back to where the function was called
    def changeReturnStemenetsAndInline(self,ast, function):
        return ast


    # TODO make it possible for multiple functions calls (now only one)
    # TODO inline multiple functions  now start with (inlining parseelt of minixml)
    # TODO ceck for infinite loops like function parseXML to parseelt to parseatt back to parseXML and fix this
    def inlineFunctions(self,ast, functionName):
        func=None
        for func in ast.ext:
            name = func.decl.name
            if name == functionName:
                foundCall=True
                self.foundCall=False
                #TODO maybe seperate this into self.setAmountOfCases(func) now it is done in the findCalls
                self.changesDeclaredVariables(func,functionName) # TODO update function of ast
                while foundCall:
                    self.foundCall=False
                    func= self.findFunctionCallsAndInlineOtherFunctions(ast,func,functionName)
                    func=self.changeProgramStepAndReturn(func, functionName)
                    foundCall=self.foundCall

                break
        return DeclerationsAndAst(self.newDeclerations,func)

    #TODO check todos inlineFunctions maybe needed here
    def findFunctionCallsAndInlineOtherFunctions(self, ast,func, function):
        self.returnTypeOfFunction=func.decl.type.type.type.names[0]
        block_items=[]
        for block in func.body.block_items:
            block_items.append(self.findCalls(block))
        tmpFunc=c_ast.FuncDef(func.decl,func.param_decls,c_ast.Compound(block_items))
        return self.inlineFunction(tmpFunc)


    def declareAllVariablesInOriginalFunction(self,ast):
        return ast

    def changeCall(self,function,functionVariableName):
        endOfSwitch=self.endOfSwitch+self.numberOfCases#TODO set amount of cases in this function
        returnToCase=self.currentCase+self.endOfSwitch #TODO is for debug purposes used to be self.currentCase+self.endOfSwitch
        declerationsArr=[]
        declerationsArr.extend(self.oldDeclerations)
        declerationsArr.extend(self.newDeclerations)

        if True:#TODO this is debug
            for func in self.ast.ext:
                name = func.decl.name
                if name == function:
                    self.foundCall = True
                    inlineFunctions = InlineFunctions(declerationsArr, endOfSwitch, self.ast, returnToCase,
                                                      functionVariableName)
                    inlineFunctions.setReturnTypeOfFynction(func.decl.type.type.type.names[0])
                    self.returnTypeOfFunction = func.decl.type.type.type.names[0]
                    func = inlineFunctions.changeProgramStepAndReturn(func, function)
                    result = DeclerationsAndAst([],func)
        else:
            inlineFunctions=InlineFunctions(declerationsArr, endOfSwitch,self.ast,returnToCase,functionVariableName)
            result = inlineFunctions.inlineFunctions(self.ast,function)
        result.setCase(self.currentCase)
        self.calls.append(result)
        self.newDeclerations.extend(result.getDeclerations())

    def findCalls(self, block):
        """if str(block).__contains__("parseatt"):
            test="""""
        match type(block):
            case c_ast.FuncCall:#TODO call this class again for the other function to flatten and add it to this one
                if self.functionInFile(block.name.name):
                    name = self.appendDecleration(block.name.name)
                    self.changeCall(block.name.name,name)
                    return c_ast.ID(name)
                else:
                    return block
            case c_ast.While:  # TODO createDoWhile (no need already in this form but should be done in flattenLoops)
                cond=self.findCalls(block.cond)
                block_items=[]
                for tempBlock in block.stmt.block_items:
                    block_items.append(self.findCalls(tempBlock))
                stmt=c_ast.Compound(block_items)
                return c_ast.While(cond,stmt)
            case c_ast.If:
                cond=self.findCalls(block.cond)
                block_items_true_case=[]
                block_items_false_case=[]
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
                return c_ast.If(cond,c_ast.Compound(block_items_true_case),c_ast.Compound(block_items_false_case))
            case c_ast.Case:
                self.currentCase = int(block.expr.value)
                if self.currentCase==19:#TODO remove DEBUG
                    pass
                cond=self.findCalls(block.expr)
                block_items=[]
                for tempBlock in block.stmts:
                    block_items.append(self.findCalls(tempBlock))
                return c_ast.Case(cond,block_items)
            case c_ast.Switch:
                if self.first:
                    self.first=False
                    self.numberOfCases=int(block.stmt.block_items[-1].expr.value)
                cond=self.findCalls(block.cond)
                block_items=[]
                for tempBlock in block.stmt.block_items:
                    block_items.append(self.findCalls(tempBlock))
                return c_ast.Switch(cond,c_ast.Compound(block_items))
            case _:  # TODO create case while not while type or if type just add to case and return it
                return block

    def replaceProgramStepAndReturn(self, block):
        valueToAdd = self.endOfSwitch  # TODO add seperation of orginal function
        match type(block):
            case c_ast.Assignment:
                if block.lvalue.name == 'programStep':
                    valueToAdd=int(block.rvalue.value)+valueToAdd
                    for call in self.calls:
                        if call.getCase()!=14: #TODO Delete this is debug
                            pass
                        if call.getCase()==int(block.rvalue.value):
                            valueToAdd=self.numberOfCases+1#TODO this one is to move to the function but if there are multiple function calls then this wouldn't work
                            break
                    #valueToAdd=1 #todo set to jump to call would be different and add seperation of orginal function
                    return c_ast.Assignment(block.op,block.lvalue,c_ast.Constant(block.rvalue.type,str(valueToAdd)))
                else:
                    return block
            case c_ast.Return:
                block_items=[]
                nameOfFunctionThatWasCalled=self.functionVariableName#TODO change this to the actual name
                jumpBack=self.returnToCase#TODO change this to the actual programStepToJumpBackTo
                if  self.returnTypeOfFunction!='void':
                    value=block.expr#'-1'#block.expr.value#'-1'#TODO change this to the actual value
                    block_items.append(c_ast.Assignment('=',c_ast.ID(nameOfFunctionThatWasCalled),value))#c_ast.Constant(returnTypeOfFunctionThatWasCalled,value)))
                block_items.append(c_ast.Assignment('=',c_ast.ID('programStep'),c_ast.Constant('int',str(jumpBack))))
                return c_ast.Compound(block_items)
            case c_ast.While:  # TODO createDoWhile (no need already in this form but should be done in flattenLoops)
                block_items=[]
                for tempBlock in block.stmt.block_items:
                    block_items.append(self.replaceProgramStepAndReturn(tempBlock))
                stmt=c_ast.Compound(block_items)
                return c_ast.While(block.cond,stmt)
            case c_ast.If:
                block_items_true_case=[]
                block_items_false_case=[]
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
                return c_ast.If(block.cond,c_ast.Compound(block_items_true_case),c_ast.Compound(block_items_false_case))
            case c_ast.Case:
                block.expr.value=str(int(block.expr.value)+valueToAdd)
                block_items=[]
                for tempBlock in block.stmts:
                    block_items.append(self.replaceProgramStepAndReturn(tempBlock))
                return c_ast.Case(block.expr,block_items)
            case c_ast.Switch:
                #block.stmt.block_items.sort(key=lambda x: int(x.expr.value))
                block_items=[]
                for tempBlock in block.stmt.block_items:
                    if tempBlock==block.stmt.block_items[-1]:
                        jumpBack = self.returnToCase  # TODO change this to the actual programStepToJumpBackTo
                        tempBlock.expr.value = str(int(tempBlock.expr.value) + valueToAdd)

                        block_items.append(c_ast.Case(tempBlock.expr,
                                                             [c_ast.Assignment('=', c_ast.ID('programStep'),
                                                                               c_ast.Constant('int', str(jumpBack)))]))
                    else:
                        block_items.append(self.replaceProgramStepAndReturn(tempBlock))
                return c_ast.Switch(block.cond,c_ast.Compound(block_items))
            case _:  # TODO create case while not while type or if type just add to case and return it
                return block

    def changeProgramStepAndReturn(self, func, function):#TODO if self.endOfSwitch==0: then only replace programSteps for the caller function
        #TODO else do this but also change the return to point back to the caller function
        """block_items = []
        for block in func.body.block_items:
            if type(block)==c_ast.While: #TODO more concrete check can check that it is actually while(run)
                block_items_while=[]
                for tempBlock in block.stmt.block_items:
                    block_items_switch=[]
                    if type(tempBlock)==c_ast.Switch:
                        lenSwitch=len(tempBlock.stmt.block_items)-1 #This is to not copy the last case (run = 0;break;)
                        for i in range(lenSwitch):
                            case=tempBlock.stmt.block_items[i]
                            block_items_switch.append(case)
                        block_items_while.append(c_ast.Switch(tempBlock.cond,c_ast.Compound(block_items_switch)))
                    else:
                        block_items_while.append(tempBlock)
                block_items.append(c_ast.While(block.cond,c_ast.Compound(block_items_while)))
            else:
                block_items.append(block)"""
        #return func
        block_items = []
        for block in func.body.block_items:
            block_items.append(self.replaceProgramStepAndReturn(block))
        tmpFunc = c_ast.FuncDef(func.decl, func.param_decls, c_ast.Compound(block_items))
        return tmpFunc #self.inlineFunction(tmpFunc)


    def appendDecleration(self, name):
        #TODO check for no conflict with already declared variables or variables in the newDeclrations
        decl=c_ast.Decl(name,None,None,None,None,c_ast.TypeDecl(name,None,None,c_ast.IdentifierType(['int'])),None,None)#TODO replace int with actually function return value if void don't add this variable
        self.newDeclerations.append(decl)
        return name


    def functionInFile(self, function):
        for func in self.ast.ext:
            name = func.decl.name
            if name == function:
                return True
        return False

    def inlineFunction(self, func):
        block_items=[]
        first =True
        block_items.extend(self.newDeclerations)
        for block in func.body.block_items:
            """if type(block) != c_ast.Decl and first:
                first = False
                block_items.extend(self.newDeclerations)
                for call in self.calls: #TODO check if this is oke for multiple calls
                    block_items.extend(call.getDeclerations())
                    self.newDeclerations.extend(call.getDeclerations())
                for call in self.calls:#TODO check if this is oke for multiple calls
                    for tempBlock in call.getFunc().body.block_items:
                        if type(tempBlock)==c_ast.TypeDecl:
                            block_items.append(tempBlock)
                            self.newDeclerations.append(tempBlock)"""

            if type(block)==c_ast.While: #TODO more concrete check can check that it is actually while(run)  #old not first and type(block)==c_ast.While
                block_items_while=[]
                for tempBlock in block.stmt.block_items:
                    block_items_switch=[]
                    if type(tempBlock)==c_ast.Switch:
                        lenSwitch=len(tempBlock.stmt.block_items)
                        for i in range(lenSwitch):
                            if i==(lenSwitch-1):
                                for call in self.calls:
                                    for tempCallBlock in call.getFunc().body.block_items:
                                        if type(tempCallBlock) == c_ast.While:
                                            for tempCallBlockWhile in tempCallBlock.stmt.block_items:
                                                if type(tempCallBlockWhile)==c_ast.Switch:
                                                    block_items_switch.extend(tempCallBlockWhile.stmt.block_items)
                                if self.endOfSwitch==0: #TODO debug test should be self.endOfSwitch==0
                                    block_items_switch.append(tempBlock.stmt.block_items[i]) #TODO only do this for the first one but update amount of cases
                                else:
                                    #block_items_switch.append(tempBlock.stmt.block_items[i])
                                    jumpBack = self.returnToCase  # TODO change this to the actual programStepToJumpBackTo
                                    block_items_switch.append(c_ast.Case(tempBlock.stmt.block_items[i].expr,[c_ast.Assignment('=', c_ast.ID('programStep'),
                                                                        c_ast.Constant('int', str(jumpBack)))]))
                            else:
                                block_items_switch.append(tempBlock.stmt.block_items[i])
                        block_items_while.append(c_ast.Switch(tempBlock.cond,c_ast.Compound(block_items_switch)))
                    else:
                        block_items_while.append(tempBlock)
                block_items.append(c_ast.While(block.cond,c_ast.Compound(block_items_while)))
            """elif type(block)==c_ast.Decl:
                    self.newDeclerations.append(block)
            else:
                block_items.append(block)"""
        #return func
        tmpFunc = c_ast.FuncDef(func.decl, func.param_decls, c_ast.Compound(block_items))
        return tmpFunc

    def setReturnTypeOfFynction(self, param):
        self.returnTypeOfFunction=param


def inlineFunctions(ast, function):
    inlineFuncClass = InlineFunctions([],0,ast,0,'')
    declerationsAndFunc=inlineFuncClass.inlineFunctions(ast, function)
    ast.ext= [declerationsAndFunc.getFunc()]
    return ast