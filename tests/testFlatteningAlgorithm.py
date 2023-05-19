import unittest

from pycparser import c_generator

from HelperFunctionsForTest import *


class TestSum(unittest.TestCase):
    def testLocalVariablesToTopOfFunction(self):
        fileName = "TestFiles/moveDeclaredVariableToTop.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestLocalVaraiblesToTopOfFunction(fileName)
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/moveDeclaredVariableToTop.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testFlattenLoopsAndLocalVariablesToTopOfFunction(self):
        fileName = "TestFiles/flattenLoopsTest.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestFlattenLoopsAndLocalVaraiblesToTopOfFunction(fileName)
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/flattenLoopsTest.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testFlattenLoopsForDoWhileAndLocalVariablesToTopOfFunction(self):
        fileName = "TestFiles/DoWhileLoopFlatteningTest.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestFlattenLoopsAndLocalVaraiblesToTopOfFunction(fileName)
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/DoWhileLoopFlatteningTest.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testFlattenLoopsInstructionOutsideLoop(self):
        fileName = "TestFiles/flattenLoopsTestInstructionsOutsideLoop.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestFlattenLoopsAndLocalVaraiblesToTopOfFunction(fileName)
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/flattenLoopsTestInstructionsOutsideLoop.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testFlattenLoopsParseelt(self):
        fileName = "TestFiles/parseelt.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestFlattenLoopsAndLocalVaraiblesToTopOfFunction(fileName)
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/parseelt.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testFlattenLoopsParseatt(self):
        fileName = "TestFiles/parseatt.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestFlattenLoopsAndLocalVaraiblesToTopOfFunction(fileName)
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/parseatt.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testInliningFunctionTest(self):
        fileName = "TestFiles/InliningFunctionTest.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestInlineFunctionAndFlattenLoopsAndLocalVaraiblesToTopOfFunction(fileName,'parsexml')
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/InliningFunctionTest.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testInliningFunctionTestCountWhiteSpaces(self):
        fileName = "TestFiles/InliningFunctionTestCountWhiteSpaces.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestInlineFunctionAndFlattenLoopsAndLocalVaraiblesToTopOfFunction(fileName,'parsexml')
        code = generator.visit(ast)

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/InliningFunctionTestCountWhiteSpaces.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testMinixml(self):
        fileName = "TestFiles/minixml.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToEntireAlgorithmAndOptimizations(fileName,'parsexml')
        code = generator.visit(ast)

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/minixml.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)


if __name__ == '__main__':
    unittest.main()
