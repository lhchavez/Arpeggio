#######################################################################
# Name: calc.py
# Purpose: Simple expression evaluator example
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009-2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# This example demonstrates grammar definition using python constructs as
# well as using semantic actions to evaluate simple expression in infix
# notation.
#######################################################################

from arpeggio import Optional, ZeroOrMore, OneOrMore, EOF, SemanticAction,\
    ParserPython
from arpeggio.export import PMDOTExporter, PTDOTExporter
from arpeggio import RegExMatch as _

def number():     return _(r'\d*\.\d*|\d+')
def factor():     return Optional(["+","-"]), [number,
                          ("(", expression, ")")]
def term():       return factor, ZeroOrMore(["*","/"], factor)
def expression(): return term, ZeroOrMore(["+", "-"], term)
def calc():       return OneOrMore(expression), EOF


# Semantic actions
class ToFloat(SemanticAction):
    """
    Converts node value to float.
    """
    def first_pass(self, parser, node, children):
        if parser.debug:
            print("Converting {}.".format(node.value))
        return float(node.value)


class Factor(SemanticAction):
    """
    Removes parenthesis if exists and returns what was contained inside.
    """
    def first_pass(self, parser, node, children):
        if parser.debug:
            print("Factor {}".format(children))
        if len(children) == 1:
            return children[0]
        sign = -1 if children[0] == '-' else 1
        next_chd = 0
        if children[0] in ['+', '-']:
            next_chd = 1
        return sign * children[next_chd]


class Term(SemanticAction):
    """
    Divides or multiplies factors.
    Factor nodes will be already evaluated.
    """
    def first_pass(self, parser, node, children):
        if parser.debug:
            print("Term {}".format(children))
        term = children[0]
        for i in range(2, len(children), 2):
            if children[i-1] == "*":
                term *= children[i]
            else:
                term /= children[i]
        if parser.debug:
            print("Term = {}".format(term))
        return term


class Expr(SemanticAction):
    """
    Adds or substracts terms.
    Term nodes will be already evaluated.
    """
    def first_pass(self, parser, node, children):
        if parser.debug:
            print("Expression {}".format(children))
        expr = 0
        start = 0
        # Check for unary + or - operator
        if str(children[0]) in "+-":
            start = 1

        for i in range(start, len(children), 2):
            if i and children[i - 1] == "-":
                expr -= children[i]
            else:
                expr += children[i]

        if parser.debug:
            print("Expression = {}".format(expr))

        return expr


# Connecting rules with semantic actions
number.sem = ToFloat()
factor.sem = Factor()
term.sem = Term()
expression.sem = Expr()

def main(debug=False):
    # First we will make a parser - an instance of the calc parser model.
    # Parser model is given in the form of python constructs therefore we
    # are using ParserPython class.
    parser = ParserPython(calc, debug=debug)

    if debug:
        # Then we export it to a dot file in order to visualise it.
        # This step is optional but it is handy for debugging purposes.
        # We can make a png out of it using dot (part of graphviz) like this
        # dot -O -Tpng calc_parse_tree_model.dot
        PMDOTExporter().exportFile(parser.parser_model,
                                "calc_parse_tree_model.dot")

    # An expression we want to evaluate
    input_expr = "-(4-1)*5+(2+4.67)+5.89/(.2+7)"

    # We create a parse tree out of textual input_expr
    parse_tree = parser.parse(input_expr)

    if debug:
        # Then we export it to a dot file in order to visualise it.
        # This is also optional.
        PTDOTExporter().exportFile(parse_tree, "calc_parse_tree.dot")

    result = parser.getASG()

    if debug:
        # getASG will start semantic analysis.
        # In this case semantic analysis will evaluate expression and
        # returned value will be the result of the input_expr expression.
        print("{} = {}".format(input_expr, result))

if __name__ == "__main__":
    main(debug=True)

