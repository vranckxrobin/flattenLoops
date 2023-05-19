import unittest

from pycparser import c_generator

from HelperFunctionsForTest import *





class TestFlattenLoops(unittest.TestCase):

    def test2Whiles(self):
        fileName = "TestFiles/flattenLoops/2Whiles.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestFlattenLoops(fileName)
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/flattenLoops/2Whiles.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testNestedWhileLoopAndIf(self):
        fileName = "TestFiles/flattenLoops/nestedWhilesAndIf.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestLocalVaraiblesToTopOfFunction(fileName)
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/flattenLoops/nestedWhilesAndIf.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testDoWhileLoop(self):
        fileName = "TestFiles/flattenLoops/WhileNestedWithDoWhile.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestLocalVaraiblesToTopOfFunction(fileName)
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/flattenLoops/WhileNestedWithDoWhile.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testAllTogether(self):
        fileName = "TestFiles/flattenLoops/all.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestLocalVaraiblesToTopOfFunction(fileName)
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/flattenLoops/all.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)


if __name__ == '__main__':
    unittest.main()
