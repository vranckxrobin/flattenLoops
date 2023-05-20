import unittest

from pycparser import c_generator

from HelperFunctionsForTest import *





class TestInliningFunctions(unittest.TestCase):

    def testInliningWhileLoops(self):
        fileName = "TestFiles/InliningLoops/Inline2Functions.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestInliningFunctions(fileName,'main')
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/InliningLoops/Inline2Functions.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testInliningWhileLoopsWithSameFunctionParameters(self):
        fileName = "TestFiles/InliningLoops/Inline2FunctionsWithSameFunctionparameter.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestInliningFunctions(fileName,'main')
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/InliningLoops/Inline2FunctionsWithSameFunctionparameter.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)
