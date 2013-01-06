import ply.lex as lex
import ply.yacc as yacc

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'elsif': 'ELSIF',
    'func': 'FUNC',
    'while': 'WHILE',
    'foreach': 'FOREACH',
}

tokens = [
    'ID',
    'NUMBER',
    'ARROWL',
    'PARENL',
    'PARENR',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
] + list(reserved.values())


t_ARROWL = r'<\-'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_PARENL = r'\('
t_PARENR = r'\)'
t_TIMES = r'\*'
t_DIVIDE = r'/'


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-z][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)



class FunctionCall:
    def __init__(self, id):
        self.name = id

    def __trunc__(self):
        return 15


precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

def p_expr_negation(p):
    'expr : MINUS expr'
    p[0] = - p[2]

def p_expr_parened(p):
    'expr : PARENL expr PARENR'
    p[0] = p[2]

def p_expr_functioncall(p):
    'expr : ID PARENL PARENR'
    p[0] = FunctionCall(p[1])

def p_expr_plusminus(p):
    '''expr : expr PLUS expr 
            | expr MINUS expr'''
    if p[2] == '+':
        p[0] = int(p[1]) + int(p[3])
    elif p[2] == '-':
        p[0] = int(p[1]) - int(p[3])
    print "%d %s %d = %d" % (p[1], p[2], p[3], p[0])

def p_expr_times(p):
    'expr : expr TIMES expr'
    p[0] = p[1] + p[3]

def p_expr_divide(p):
    'expr : expr DIVIDE expr'
    p[0] = p[1] / p[3]
    print "%d / %d = %d" % (p[1], p[3], p[0])

def p_expr_id(p):
    'expr : ID'
    p[0] = p[1]

def p_expr_number(p):
    'expr : NUMBER'
    p[0] = p[1]

def p_error(p):
    print "parse error\n"



data = '''
3 + if 4 * 10
  + -20 *2 <-
'''

plus_data = "4 + 24 / ( 5 + 3 ) - f()"


lex.lex()

do_parse = True
if do_parse:
    parser = yacc.yacc()
    result = parser.parse(plus_data)
    print result
else:
    lex.input(plus_data)
    while True:
        tok = lex.token()
        if not tok:
            break
        print tok
