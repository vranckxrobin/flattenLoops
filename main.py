from inlineFunction import  inlineFunctions
from localVariablesToTopOfFunction import *
from flattenLoops import *
from pycparser import parse_file, c_generator
import re
from optimizations import replaceSwitch


class FuncDefVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.nodes = []

    def getFunctionNodes(self):
        return self.nodes

    def visit_FuncDef(self, node):
        print(f'{node.decl.name} at {node.decl.coord}')
        self.nodes.append(node)

def extractIncludes(filename):
    includes = ""

    with open(filename) as file:
        for line in file:
            if re.search("#include", line):
                includes += line
    return includes


def generateFunctionsAST(ast):
    v = FuncDefVisitor()
    v.visit(ast)
    ast.ext = v.getFunctionNodes()
    return ast


def ASTToCfile(ast, filename,function):
    generator = c_generator.CGenerator()

    ast = generateFunctionsAST(ast)
    ast = allLocalVariablesAtTopOfFunction(ast)
    ast = flattenLoopsForAllFunction(ast)
    ast = inlineFunctions(ast, function)
    ast = replaceSwitch(ast,function)

    codeWithoutIncludes = generator.visit(ast)

    includes = extractIncludes(filename)  # TODO extract everything that is not a function (example global variables)
    if '#include <stdbool.h>\n' not in includes:
        includes += '#include <stdbool.h>\n'

    with open("flatten2.c", "w") as f:
        f.write(includes + codeWithoutIncludes)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        filename = sys.argv[1]
        function = sys.argv[2]
    else:
        filename = 'minixml.c'  # 'smallLoopTest.c''cprogramTest1.c'minixml.c''parseelt.c'
        function='parsexml'
    # ast=parse_file(filename)
    ast = parse_file(filename, use_cpp=True,
                     cpp_path='cpp',
                     cpp_args=r'-Ipycparser-master/utils/fake_libc_include')

    ASTToCfile(ast, filename,function)
