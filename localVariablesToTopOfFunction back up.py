# -----------------------------------------------------------------
# pycparser: using_cpp_libc.py
#
# Shows how to use the provided 'cpp' (on Windows, substitute for
# the 'real' cpp if you're on Linux/Unix) and "fake" libc includes
# to parse a file that includes standard C headers.
#
# Eli Bendersky [https://eli.thegreenplace.net/]
# License: BSD
# -----------------------------------------------------------------
import sys

# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
#

sys.path.extend(['.', '..'])

from pycparser import parse_file, c_generator, c_ast
import re

declerations=[]

class FuncDefVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.nodes = []

    def getFunctionNodes(self):
        return self.nodes

    def visit_FuncDef(self, node):
        print('%s at %s' % (node.decl.name, node.decl.coord))
        self.nodes.append(node)


def extractIncludes(filename):
    includes = ""

    with open(filename) as file:
        for line in file:
            if (re.search("#include", line)):
                includes += line
    return includes


def generateFunctionsAST(ast):
    v = FuncDefVisitor()
    v.visit(ast)
    ast.ext = v.getFunctionNodes()
    return ast

def getDefaultValue(type):
    #TODO support other types if necessary
    return c_ast.Constant('string',"\"\"")

def typesForBlockItems(block):
    match type(block):
        case c_ast.Decl:
            global declerations
            declerations.append(block)
            return c_ast.Assignment('=', c_ast.ID(block.name),getDefaultValue(block.type))
        case c_ast.While:
            return c_ast.While(block.cond,blockItemsLoop(getattr(getattr(block, 'stmt', None), 'block_items', [])),block.coord)
        case c_ast.DoWhile:
            return c_ast.DoWhile(block.cond,blockItemsLoop(getattr(getattr(block, 'stmt', None), 'block_items', [])),block.coord)
        case c_ast.If:
            ifblock=c_ast.If(block.cond,None,None,block.coord)
            if c_ast.Compound==type(block.iffalse):
                ifblock.iffalse=c_ast.Compound(blockItemsLoop(getattr(getattr(block, 'iffalse', None), 'block_items', [])),block.coord)
            elif c_ast.If ==type(block.iffalse):
                ifblock.iffalse =typesForBlockItems(block.iffalse)
            else:
                ifblock.iffalse =block.iffalse
            if c_ast.Compound==type(block.iftrue):
                ifblock.iftrue=c_ast.Compound(blockItemsLoop(getattr(getattr(block, 'iftrue', None), 'block_items', [])),block.coord)
            elif c_ast.If ==type(block.iftrue):
                ifblock.iftrue =typesForBlockItems(block.iftrue)
            else:
                ifblock.iftrue =block.iftrue
            return ifblock
        case _:
            return block


def blockItemsLoop(block_items):
    newBlockItems=c_ast.Compound([],None)
    for block in block_items:
        newBlockItems.block_items.append(typesForBlockItems(block))
    return newBlockItems

def allLocalVariablesAtTopOfFunction(ast):
    newAst=c_ast.FileAST([],ast.coord)
    for funcDef in ast.ext:
        block_items = getattr(getattr(funcDef, 'body', None), 'block_items', [])
        lastDecleration = 0
        lastFound=False
        newBody=c_ast.Compound([],funcDef.body.coord)
        global declerations
        declerations=[]
        for block in block_items:
            if(not(lastFound)):
                if c_ast.Decl != type(block):
                    newBody.block_items.append(typesForBlockItems(block))
                    lastFound=True
                else:
                    newBody.block_items.append(block)
                    lastDecleration += 1
            else:
                newBody.block_items.append(typesForBlockItems(block))
        for decleration in declerations:
            newBody.block_items.insert(lastDecleration,decleration)
        newFuncDef=c_ast.FuncDef(funcDef.decl,funcDef.param_decls,newBody,funcDef.coord)
        newAst.ext.append(newFuncDef)
    return newAst


def ASTToCfile(ast, filename):
    generator = c_generator.CGenerator()

    ast = generateFunctionsAST(ast)
    ast = allLocalVariablesAtTopOfFunction(ast)

    codeWithoutIncludes = generator.visit(ast)

    includes = extractIncludes(filename)  # TODO extract everything that is not a function (example global variables)

    f = open("test2.c", "w")
    f.write(includes + codeWithoutIncludes)
    f.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'minixml.c'#'cprogramTest1.c'minixml.c'
    #ast=parse_file(filename)
    ast = parse_file(filename, use_cpp=True,
                     cpp_path='cpp',
                     cpp_args=r'-Ipycparser-master/utils/fake_libc_include')

    ASTToCfile(ast, filename)

