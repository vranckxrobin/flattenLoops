import unittest

from pycparser import c_generator

from HelperFunctionsForTest import *


class TestMovingVariablesToTop(unittest.TestCase):

    def testIf(self):
        fileName = "TestFiles/localVariablesToTopOfFunction/if.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestLocalVaraiblesToTopOfFunction(fileName)
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/localVariablesToTopOfFunction/if.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testWhileLoop(self):
        fileName = "TestFiles/localVariablesToTopOfFunction/while.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestLocalVaraiblesToTopOfFunction(fileName)
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/localVariablesToTopOfFunction/while.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testDoWhileLoop(self):
        fileName = "TestFiles/localVariablesToTopOfFunction/doWhile.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestLocalVaraiblesToTopOfFunction(fileName)
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/localVariablesToTopOfFunction/doWhile.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testAllTogether(self):
        fileName = "TestFiles/localVariablesToTopOfFunction/all.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestLocalVaraiblesToTopOfFunction(fileName)
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/localVariablesToTopOfFunction/all.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)


if __name__ == '__main__':
    unittest.main()
