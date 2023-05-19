from pycparser import parse_file, c_ast

from flattenLoops import flattenFile
from inlineFunction import inlineFunctions
from localVariablesToTopOfFunction import allLocalVariablesToTopOfFunctions
from main import extractIncludes
from optimizations import replaceSwitch


def helperFunctionCreateAst(filename):
    return parse_file(filename, use_cpp=True,
                      cpp_path='cpp',
                      cpp_args=r'-I../pycparser-master/utils/fake_libc_include')


def helperFunctionGetIncludes(filename):
    includes = extractIncludes(
        filename)
    if '#include <stdbool.h>\n' not in includes:
        includes += '#include <stdbool.h>\n'
    return includes


def helperFunctionToTestLocalVaraiblesToTopOfFunction(filename):
    ast = helperFunctionCreateAst(filename)
    helperFunctionCreateAst(filename)
    # Apply the algorithm to the abstract syntax tree
    return allLocalVariablesToTopOfFunctions(ast)


def helperFunctionToTestFlattenLoopsAndLocalVaraiblesToTopOfFunction(filename):
    ast = helperFunctionToTestLocalVaraiblesToTopOfFunction(filename)
    return flattenFile(ast)


def helperFunctionToTestInlineFunctionAndFlattenLoopsAndLocalVaraiblesToTopOfFunction(filename, function):
    ast = helperFunctionToTestFlattenLoopsAndLocalVaraiblesToTopOfFunction(filename)
    return inlineFunctions(ast, function)


def helperFunctionToEntireAlgorithmAndOptimizations(filename, function):
    ast = helperFunctionToTestInlineFunctionAndFlattenLoopsAndLocalVaraiblesToTopOfFunction(filename, function)
    return replaceSwitch(ast, function)


def helperFunctionToTestFlattenLoops(fileName):
    ast = helperFunctionCreateAst(fileName)
    return flattenFile(ast)

def helperFunctionToTestInliningFunctions(fileName,func):
    ast = helperFunctionCreateAst(fileName)
    ast = c_ast.FileAST([func for func in ast.ext if isinstance(func, c_ast.FuncDef)])
    return inlineFunctions(ast,func)
