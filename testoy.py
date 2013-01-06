import ply.lex as lex
import ply.yacc as yacc

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'elsif': 'ELSIF',
    'end': 'END',
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
    'COMMA',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'NEWLINE',
] + list(reserved.values())


t_ARROWL = r'<\-'
t_COMMA = r','
t_DIVIDE = r'/'
t_MINUS = r'\-'
t_PARENL = r'\('
t_PARENR = r'\)'
t_PLUS = r'\+'
t_TIMES = r'\*'


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-z][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

t_ignore = ' \t'

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)



class FunctionDef:
    def __init__(self, id, args, stmts):
        self.name = id
        self.args = args
        self.code = stmts

    def __repr__(self):
        r = "func:%s(" % self.name
        first = True
        for a in self.args:
            if not first:
                r += ","
            else:
                first = False
            r += a
        r += ")"
        return r

class AssignStmt:
    def __init__(self, id, expr):
        self.dst = id
        self.src = expr

class FunctionCall:
    def __init__(self, id, args):
        self.name = id
        self.args = args

    def __trunc__(self):
        sum = 0
        for arg in self.args:
            sum += arg
        return sum


start = 'program'

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)


def p_program(p):
    'program : topstmts'
    p[0] = p[1]

def p_topstmts_first(p):
    'topstmts : topstmt'
    p[0] = [p[1]]

def p_topstmts_more(p):
    'topstmts : topstmts topstmt'
    p[0] = p[1]
    p[0].append(p[2])

def p_topstmt_func(p):
    'topstmt : FUNC ID PARENL optcallargs PARENR NEWLINE code END NEWLINE'
    p[0] = FunctionDef(p[2], p[4], p[6])

def p_code_first(p):
    'code : stmteol'
    p[0] = [p[1]]

def p_code_more(p):
    'code : code stmteol'
    p[0] = p[1]
    p[0].append(p[2])


def p_stmteol(p):
    'stmteol : stmt NEWLINE'
    p[0] = p[1]

def p_stmt_assign(p):
    'stmt : ID ARROWL expr'
    p[0] = AssignStmt(p[1], p[3])
    print 'found assign stmt'


def p_empty(p):
    'empty :'
    pass

def p_expr_negation(p):
    'expr : MINUS expr'
    p[0] = - p[2]

def p_expr_parened(p):
    'expr : PARENL expr PARENR'
    p[0] = p[2]

def p_expr_functioncall(p):
    'expr : ID PARENL optcallargs PARENR'
    p[0] = FunctionCall(p[1], p[3])

def p_optcallargs_notempty(p):
    'optcallargs : callargs'
    p[0] = p[1]

def p_optcallargs_empty(p):
    'optcallargs : empty'
    p[0] = []

def p_callargs_first(p):
    'callargs : expr'
    p[0] = [p[1]]
    print "found callargs: %s" % p[1]

def p_callargs_more(p):
    'callargs : callargs COMMA expr'
    p[0] = p[1]
    p[0].append(p[3])

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
    print "parse error: %s" % str(p)


def interpret(program):
    f


data = '''
3 + if 4 * 10
  + -20 *2 <-
'''

plus_data = "sum(9,3) + 24 / ( 5 + 3 ) - f(5)"

sample1 = '''func main(tacos)
    x <- 5
end
'''


lex.lex()

cmd = 'p'
if cmd == 'x':
    parser = yacc.yacc()
    ast = parser.parse(sample1)
    program = compile(ast)
    interpret(program)
elif cmd == 'p':
    parser = yacc.yacc()
    result = parser.parse(sample1)
    print result
else:
    lex.input(sample1)
    while True:
        tok = lex.token()
        if not tok:
            break
        print tok
