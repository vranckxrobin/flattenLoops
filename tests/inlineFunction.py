import unittest

from pycparser import c_generator

from HelperFunctionsForTest import *





class TestInliningFunctions(unittest.TestCase):

    def testInliningWhileLoops(self):
        fileName = "TestFiles/InliningLoops/flattenLoopsTest.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestFlattenLoopsAndLocalVaraiblesToTopOfFunction(fileName)
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/InliningLoops/flattenLoopsTest.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)


if __name__ == '__main__':
    unittest.main()
