from typing import Union
from pycparser import c_ast

Expression = Union[
    c_ast.ArrayRef, c_ast.Assignment, c_ast.BinaryOp, c_ast.Cast, c_ast.CompoundLiteral, c_ast.Constant,
    c_ast.ExprList, c_ast.FuncCall, c_ast.ID, c_ast.StructRef, c_ast.TernaryOp, c_ast.UnaryOp]

Statement = Union[
    Expression, c_ast.Break, c_ast.Case, c_ast.Compound, c_ast.Continue, c_ast.Decl, c_ast.Default,
    c_ast.DoWhile, c_ast.EmptyStatement,c_ast.For, c_ast.Goto, c_ast.If, c_ast.Label, c_ast.Return,
    c_ast.Switch, c_ast.Typedef, c_ast.While, c_ast.Pragma]