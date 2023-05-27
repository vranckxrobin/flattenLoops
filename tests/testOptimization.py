import unittest

from pycparser import c_generator

from HelperFunctionsForTest import *


class TestOptimization(unittest.TestCase):

    def testReplaceSwitch(self):
        fileName = "TestFiles/optimization/cases.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestOptimization(fileName,"main")
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/optimization/cases.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

    def testReplaceMemcmpAndConvertToIFStatements(self):
        fileName = "TestFiles/optimization/testMemcmp.c"
        generator = c_generator.CGenerator()
        ast = helperFunctionToTestOptimization(fileName,"main")
        code = generator.visit(ast)  # Convert abstract syntax tree to C code

        code = helperFunctionGetIncludes(fileName) + code
        with open("TestFilesResult/optimization/testMemcmp.c", "r") as f:
            result = f.read()
        self.assertEqual(code, result)

