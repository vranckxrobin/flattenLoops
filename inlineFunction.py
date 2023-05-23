from pycparser import c_ast


# Class datatype of tupel of decleration and name
class DeclAndReplaceName:
    def __init__(self, decleration, name):
        self.decleration = decleration
        self.name = name


# Class datatype that contains declerations, a function, the currentCase and the argument for that function
class DeclerationsAndFunc(object):
    def __init__(self, declerations, func):
        self.declerations = declerations
        self.func = func
        self.currentCase = 0
        self.callingArgs = []

    def getDeclerations(self):
        return self.declerations

    def getFunc(self):
        return self.func

    def setCase(self, currentCase):
        self.currentCase = currentCase

    def getCase(self):
        return self.currentCase

    def setCallingArguments(self, params):
        self.callingArgs = params

    def getCallingArguments(self):
        return self.callingArgs


# Class responsible for inlining of a function
class InlineFunctions:
    def __init__(self, declerations, endOfSwitch, ast, returnToCase, functionVariableName):
        self.oldDeclerations = declerations  # Declared variables
        self.endOfSwitch = endOfSwitch  # Last switch case
        self.ast = ast  # The abstract syntax tree to get other functions from
        self.returnToCase = returnToCase  # To which case to return to

        # The name of the variable that the function will need to set when it returns.
        self.functionVariableName = functionVariableName

        self.parameters = []  # Parameters of this function
        self.newDeclerations = []  # New variables to declare for this function
        self.calls = []  # Other functions that are called
        self.currentCase = 0  # The current case number

        # Variables that need to have a new name for this function
        # because the functions above it in the ast already has that name
        self.replaceVariable = []
        self.callerFunctionParameters = []  # Parameters from the function that this function calls
        self.setParams = False  # When to set the parameters to call the function

    # Changes declaration of variables if necessary, if they are not declared yet, then they can just be added
    def changesDeclaredVariables(self, func):
        for block in func.body.block_items:
            if type(block) == c_ast.Decl:
                if not self.isInOldDeclerations(block.name):  # Check if already declared
                    self.newDeclerations.append(block)
                elif block.name not in ['run', 'programStep']:
                    self.replaceVariableAndDeclare(block)

    # Find  and replace the declname
    def blockReplaceDeclName(self, block, name):
        if hasattr(block, 'declname'):
            block.declname = name
        else:
            block.type = self.blockReplaceDeclName(block.type, name)

        return block

    # Add _2 to the name of a variable until the name is not found in the declarations
    # of the function that called this function or is already present in this function
    # Then add this to the variables that need to be replaced
    def replaceVariableAndDeclare(self, block):
        name = block.name
        name += "_2"
        while self.isInOldOrNewDeclerations(name):
            name += "_2"

        self.replaceVariable.append(DeclAndReplaceName(block.name, name))
        block = self.blockReplaceDeclName(block, name)
        block.name = name
        self.newDeclerations.append(block)
        return name

    # Check if variable name is in the variables of the function that called this function
    def isInOldDeclerations(self, name):
        return any(decl.name == name for decl in self.oldDeclerations)

    # Check if variable name is in the variables of the function that called this function
    # or is already used in this declaration
    def isInOldOrNewDeclerations(self, name):
        return self.isInOldDeclerations(name) or any(decl.name == name for decl in self.newDeclerations)

    # Inline  a function
    def inlineFunction(self, func):
        self.functionParams = getattr(func.decl.type.args, 'params',
                                      [])
        self.declareParameters()
        self.changesDeclaredVariables(func)
        func = self.findFunctionCallsAndInlineOtherFunctions(func)
        return self.changeProgramStepAndReturn(func)

    # Find the function to inline and call the inlineFunction function
    def findFunctionAndInline(self, functionName):
        func = next(func for func in self.ast.ext if func.decl.name == functionName)
        return DeclerationsAndFunc(self.newDeclerations, self.inlineFunction(func))

    # Find all of the functions that will be called, and inline them into this function.
    def findFunctionCallsAndInlineOtherFunctions(self, func):
        self.returnTypeOfFunction = func.decl.type.type.type.names[0]
        block_items = [self.findCalls(block) for block in func.body.block_items]
        tmpFunc = c_ast.FuncDef(func.decl, func.param_decls, c_ast.Compound(block_items))
        return self.inlineFunctionCall(tmpFunc)

    # Inline a function call
    def changeCall(self, function, functionVariableName, args):
        # ReturnToCase is the number of cases for this function + the end of the caller function switch
        returnToCase = self.currentCase + self.endOfSwitch
        # All declaration from this function and the function that called it
        declerationsArr = self.oldDeclerations + self.newDeclerations

        # Inline of function
        inlineFunctions = InlineFunctions(declerationsArr, self.numberOfCases, self.ast, returnToCase,
                                          functionVariableName)
        # if args is not None:
        #      inlineFunctions.setCallerFunctionParameters([arg.name for arg in args.exprs])
        result = inlineFunctions.findFunctionAndInline(function)

        result.setCase(self.currentCase)  # Set case to where this function was called
        result.setCallingArguments(args.exprs)  # Set case to where this function was called

        # get parameters to set the parameters of this function
        self.callerFunctionParameters = inlineFunctions.getParameters()
        self.calls.append(result)  # append to function that was called
        # Add the declarations of this new function to the new declaration
        self.newDeclerations.extend(result.getDeclerations())

    # Find calls for one case of the if statement (true case or false case)
    # and find function calls
    def ifBodyCase(self, ifBodyCase):
        if isinstance(ifBodyCase, c_ast.Compound):
            return [self.findCalls(tempBlock) for tempBlock in ifBodyCase.block_items]
        else:
            return [self.findCalls(ifBodyCase)]

    # Look for calls in a statement and when found, call changeCall function
    # and replace the function call with an id of the new function variable
    def findCalls(self, block):
        match type(block):
            case c_ast.FuncCall:
                if not self.functionInFile(block.name.name):
                    return block
                name = self.appendFunction(block.name.name)
                self.changeCall(block.name.name, name, block.args)
                if name == "":  # for void function that it doesn't return anything
                    return
                else:
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
                block_items += [self.findCalls(tempBlock) for tempBlock in block.stmts]
                return c_ast.Case(self.findCalls(block.expr), block_items)
            case c_ast.Switch:
                self.numberOfCases = int(block.stmt.block_items[-1].expr.value)
                return c_ast.Switch(self.findCalls(block.cond),
                                    c_ast.Compound([self.findCalls(tempBlock) for tempBlock in block.stmt.block_items]))
            case _:  #
                return block

    # Call the replaceProgramStepAndReturn function for all statements in an if case (true or false case)
    def replaceProgramStepAndReturnIfCase(self, ifBodyCase):
        if isinstance(ifBodyCase, c_ast.Compound):
            return [self.replaceProgramStepAndReturn(tempBlock) for tempBlock in ifBodyCase.block_items]
        else:
            return [self.replaceProgramStepAndReturn(ifBodyCase)]

    # Add the endOfSwitch value to the programSteps to be able to add it to the function that called this one
    # Change the return statement to return to the calling function
    # And change the program step from a function call to jump to the starting case of the function
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
                    )  # Original  return block
                if not self.setParams and any(call.getCase() == int(block.rvalue.value) for call in self.calls):
                    call = next(call for call in self.calls if call.getCase() == int(block.rvalue.value))
                    self.functionParams = call.getCallingArguments()
                self.setParams = (
                        self.setParams or any(call.getCase() == int(block.rvalue.value) for call in self.calls))
                valueToAdd = self.numberOfCases + 1 + self.endOfSwitch if any(
                    call.getCase() == int(block.rvalue.value) for call in self.calls) else valueToAdd + int(
                    block.rvalue.value)  # Compute the program step for the function call to jump to
                return c_ast.Assignment(
                    block.op,
                    block.lvalue,
                    c_ast.Constant(block.rvalue.type, str(valueToAdd)),
                )
            case c_ast.Return:
                # Change the return statement to return to the calling function
                if self.functionVariableName is None:
                    return c_ast.Return(block.expr)
                block_items = [
                    c_ast.Assignment('=', c_ast.ID('programStep'), c_ast.Constant('int',
                                                                                  str(self.returnToCase)))]
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
                block.expr.value = str(int(block.expr.value) + valueToAdd)
                # Replace last case to end the loop to just jump back to the function that called this one
                if getattr(getattr(block.stmts[0], 'lvalue', None), 'name', "") == "run" and self.endOfSwitch != 0:
                    block_items = [c_ast.Compound([c_ast.Assignment('=', c_ast.ID('programStep'), c_ast.Constant('int',
                                                                                                                 str(self.returnToCase)), )]),
                                   c_ast.Break()]
                else:
                    block_items = [self.replaceProgramStepAndReturn(tempBlock) for tempBlock in block.stmts]
                if self.setParams and len(
                        self.functionParams) > 0:  # Add setting of the parameters to call functions to this case
                    block_items = block_items[:(len(block_items) - 2)] + \
                                  [c_ast.Assignment('=', c_ast.ID(param), c_ast.ID(self.functionParams[i].name)) for
                                   i, param in
                                   enumerate(self.callerFunctionParameters)] + block_items[len(block_items) - 2:]
                    self.setParams = False
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

    # Call replaceProgramStepAndReturn for each statement in the function body
    def changeProgramStepAndReturn(self, func):
        return c_ast.FuncDef(func.decl, func.param_decls, c_ast.Compound(
            [self.replaceProgramStepAndReturn(block) for block in func.body.block_items]))

    # Find function
    def findFunction(self, functionName):
        return next(func for func in self.ast.ext if func.decl.name == functionName)

    # Add the name of the function and it type to the declerations list
    def appendFunction(self, name):
        func = self.findFunction(name)
        type = func.decl.type.type.type.names[0]
        if type == "void":
            return ""
        decl = c_ast.Decl(name, None, None, None, None, c_ast.TypeDecl(name, None, None, c_ast.IdentifierType([type])),
                          None,
                          None)  # TODO replace int with actually function return value if void don't add this variable
        self.newDeclerations.append(decl)
        return name

    # See if the function is declared in the supplied file
    def functionInFile(self, function):
        return any(func.decl.name == function for func in self.ast.ext)

    # Get all cases from the function call
    def getSwitchCasesFromCall(self, call):
        functionWhileLoop = next(
            block for block in call.getFunc().body.block_items if isinstance(block, c_ast.While))
        functionSwitch = next(
            tempCallBlockWhile for tempCallBlockWhile in functionWhileLoop.stmt.block_items if
            isinstance(tempCallBlockWhile, c_ast.Switch))
        return functionSwitch.stmt.block_items

    # flatten list from list to list
    def flatten(self, list):
        return [element for sublist in list for element in sublist]

    # Add inlined function cases to this function
    def inlineFunctionCall(self, func):
        whileLoop = next(block for block in func.body.block_items if type(block) == c_ast.While)
        switch = next(block for block in whileLoop.stmt.block_items if isinstance(block, c_ast.Switch))

        lenSwitch = len(switch.stmt.block_items) - 1
        # Add function cases
        block_items_switch = switch.stmt.block_items[:lenSwitch] + \
                             self.flatten([self.getSwitchCasesFromCall(call) for call in self.calls]) + \
                             [switch.stmt.block_items[lenSwitch]]

        # Add new declarations
        block_items = self.newDeclerations + [c_ast.While(whileLoop.cond,
                                                          c_ast.Compound([c_ast.Switch(switch.cond, c_ast.Compound(
                                                              block_items_switch))]))]
        return c_ast.FuncDef(func.decl, func.param_decls, c_ast.Compound(block_items))  # return new function

    # Get parameters
    def getParameters(self):
        return self.parameters

    # def setCallerFunctionParameters(self,parameters):
    #      self.functionParams=parameters

    # Add parameter to declarations and change name if necessary
    # then add this name to the self.parameters array
    def declareParameters(self):
        if self.returnToCase != 0:
            for functionParam in self.functionParams:
                if all(x.name != functionParam.name for x in self.oldDeclerations):
                    name = functionParam.name
                    self.newDeclerations.append(
                        c_ast.Decl(functionParam.name, None, None, None, None, functionParam.type, None, None))
                else:
                    name = self.replaceVariableAndDeclare(functionParam)
                self.parameters.append(name)


# Inlining of functions
def inlineFunctions(ast, function):
    inlineFuncClass = InlineFunctions([], 0, ast, 0, None)
    declerationsAndFunc = inlineFuncClass.findFunctionAndInline(function)
    return c_ast.FileAST([declerationsAndFunc.getFunc()])
