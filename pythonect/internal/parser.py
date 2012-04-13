import ply.yacc as yacc
import logging


# Local imports

import lexer


# tokens for parser

tokens = lexer.tokens


##################
# Parser Functions
##################

def p_program(p):
    '''program : expr_list
               | empty'''

    # program : expression

    if p[1]:

        p[0] = p[1]

    else:

    # program : empty

        p[0] = []


def p_empty(p):
    '''empty :'''

    pass


def p_expr_list(p):
    '''expr_list : expr_list COMMA expr
                 | expr'''

    # expr_list : expr_list COMMA expr

    if len(p) == 4:

        p[0] = p[1] + [p[3]]

    # expr_list : expr

    else:

        p[0] = [p[1]]


def p_expr(p):
    '''expr : expr OPERATOR atom
            | atom'''

    # expr : expr

    if len(p) == 4:

        p[0] = p[1] + [[p[2], p[3]]]

        # TODO: This is an ugly patch, swap OPERATOR's

        # [ ['None, 'Hello'] , ['->'World'] ] to [ ['->', 'Hello'],['None','World'] ]

        p[0][-2][0], p[0][-1][0] = p[0][-1][0], p[0][-2][0]

    # expr : atom

    else:

        p[0] = [[None, p[1]]]


def p_atom(p):
    '''atom : PYTHON_EXPRESSION
            | PYTHON_STATEMENT'''

    p[0] = p[1]


def p_error(p):

    raise SyntaxError("Syntax error in input!")


##############
# Parser Class
##############

class Parser(object):

    def __init__(self, stmt_as_is=False):

        self.lexer = lexer.Lexer(stmt_as_is)

        # TODO: `write_tables=0` is a temporary workaround until we find a directory to settle in

        self.parser = yacc.yacc(start="program", debug=True, debuglog=logging.getLogger('parser'), errorlog=logging.getLogger('parser2'), write_tables=0)

    def parse(self, code):

        # Go!

        self.lexer.lexer.input(code)

        return self.parser.parse(lexer=self.lexer.lexer, debug=logging.getLogger('parse'))
