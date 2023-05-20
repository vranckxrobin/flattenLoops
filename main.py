from inlineFunction import inlineFunctions
from localVariablesToTopOfFunction import *
from flattenLoops import *
from pycparser import parse_file, c_generator
import re
from optimizations import replaceSwitch


# # Class to get only the function from an abstract syntax tree
# class FuncDefVisitor(c_ast.NodeVisitor):
#     def __init__(self):
#         self.nodes = []
#
#     def getFunctionNodes(self):
#         return self.nodes
#
#     def visit_FuncDef(self, node):
#         print(f'{node.decl.name} at {node.decl.coord}')
#         self.nodes.append(node)


# Find all includes in the file
def extractIncludes(filename):
    includes = ""

    with open(filename) as file:
        for line in file:
            if re.search("#include", line):
                includes += line
    if '#include <stdbool.h>\n' not in includes:
        includes += '#include <stdbool.h>\n'
    return includes


# Extract function from abstract syntax tree
# def generateFunctionsAST(ast):
#     v = FuncDefVisitor()
#     v.visit(ast)
#     ast.ext = v.getFunctionNodes()
#     return ast


# Apply the algorithm to the abstract syntax tree
# Convert abstract syntax tree to C code and add includes
def ASTToCfile(ast, filename, function):
    generator = c_generator.CGenerator()
    # ast = generateFunctionsAST(ast)

    # Apply the algorithm to the abstract syntax tree
    ast = allLocalVariablesToTopOfFunctions(ast)
    ast = flattenFile(ast)
    ast = inlineFunctions(ast, function)
    ast = replaceSwitch(ast, function)

    codeWithoutIncludes = generator.visit(ast)  # Convert abstract syntax tree to C code

    # Add includes
    includes = extractIncludes(filename)  # TODO extract everything that is not a function (example global variables)

    with open("flatten3.c", "w") as f:
        f.write(includes + codeWithoutIncludes)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        filename = sys.argv[1]
        function = sys.argv[2]
    else:
        filename = 'minixml.c'  # 'smallLoopTest.c''cprogramTest1.c'minixml.c''parseelt.c'
        function = 'parsexml'

    ast = parse_file(filename, use_cpp=True,
                     cpp_path='cpp',
                     cpp_args=r'-Ipycparser-master/utils/fake_libc_include')

    ASTToCfile(ast, filename, function)
