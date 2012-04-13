import ply.lex as lex
import logging


# Local imports

import preprocessor


########
# Tokens
########

tokens = [
        'PYTHON_STATEMENT',
        'PYTHON_EXPRESSION',
        'OPERATOR',
        'COMMA'
]


t_COMMA = r'\,'

t_OPERATOR = r'(\-\>|\|)'


def t_SOURCE(t):
    r'[^(\-\>|\|\#|\,)].*'

    scope = 0

    token_lexpos = 0

    dquotes = 0

    squotes = 0

    # i.e. 0 if token is "1" in "1 -> print" and 5 if token is "print" in "1 -> print"

    # TODO: .find() overlapping in `1 -> 1 -> 1`, .rfind() not, is .rfind() safe?

    relative_lexpos = t.lexer.lexdata.rfind(t.value)

    # Iterate token

    while token_lexpos < len(t.value):

        char = t.value[token_lexpos]

        # " ... " or ' ... ' ?

        if dquotes or squotes:

            if char == '\"':

                dquotes = dquotes - 1

            if char == '\'':

                squotes = squotes - 1

            # Ignore other characters

        else:

            # `[]` , `()` and '{}'

            if char == '[' \
            or char == '(' \
            or char == '{':

                scope = scope + 1

            if char == ']' \
            or char == ')' \
            or char == '}':

                scope = scope - 1

            # `"` and `'`

            if char == '\"':

                dquotes = dquotes + 1

            if char == '\'':

                squotes = squotes + 1

            # i.e. `... X` and not `[ ... X ]` , `( ... X )` ' { ... X } ' , `" ... X"` or `' ... X'`

            if not dquotes and not squotes and not scope:

                # Comma

                if char == ',':

                    # END OF TOKEN (i.e. 1 -> print , ... )

                    break

                # Operator

                if char == '|' or \
                        (char == '-' and token_lexpos + 1 < len(t.value) and t.value[token_lexpos + 1] == '>'):

                    # END OF TOKEN (i.e. 1 -> ...)

                    break

        token_lexpos = token_lexpos + 1

    # Break?

    if token_lexpos != len(t.value):

        # Calculate a new lexpos

        t.lexer.lexpos = relative_lexpos + token_lexpos

    # Send strip()'ed token to preprocessor

    t.type, t.value = preprocessor.preprocessor(t.value[:token_lexpos].rstrip(), stmt_as_is=t.lexer.stmt_as_is)

    return t


# Ignore list

t_ignore = ' \n'

t_ignore_COMMENT = r'\#.*'


# Error-handler

def t_error(t):

    print "Illegal character '%s'" % (t.value[0])

    t.lexer.skip(1)


#############
# Lexer Class
#############

class Lexer(object):

    def __init__(self, stmt_as_is=False):

        self.lexer = lex.lex(debug=True, debuglog=logging.getLogger('lex'), errorlog=logging.getLogger('lex2'))

        # Lexer-specific settings

        self.lexer.stmt_as_is = stmt_as_is
