import ply.lex as lex
import ply.yacc as yacc

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'elsif': 'ELSIF',
    'end': 'END',
    'func': 'FUNC',
    'return': 'RETURN',
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


class VarExpr:
    def __init__(self, id):
        self.name = id

    def evaluate(self, prog):
        return prog.get(self.name)

    def __repr__(self):
        return str(self.name)

class ConstIntExpr:
    def __init__(self, val):
        self.value = val

    def evaluate(self, prog):
        return self.value

    def __repr__(self):
        return str(self.value)

class BinaryExpr:
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def evaluate(self, prog):
        val1 = self.op1.evaluate(prog)
        val2 = self.op2.evaluate(prog)
        return self.operate(val1, val2)

    def __repr__(self):
        op1_str = str(self.op1)
        op2_str = str(self.op2)
        return "%s %s %s" % (op1_str, self.operator_string(), op2_str)

class AddExpr(BinaryExpr):
    def operate(self, a, b):
        return a + b

    def operator_string(self):
        return '+'

class MultExpr(BinaryExpr):
    def operate(self, a, b):
        return a * b

    def operator_string(self):
        return '*'


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

    def print_code(self):
        print str(self)
        for i in self.code:
            print "\t%s" % str(i)


class AssignStmt:
    def __init__(self, id, expr):
        self.dst = id
        self.src = expr

    def __repr__(self):
        return "%s <- %s" % (self.dst, self.src)

    def execute(self, prog):
        val = self.src.evaluate(prog)
        prog.set_local(self.dst, val)

class ReturnStmt:
    def __init__(self, expr):
        self.expr = expr

    def execute(self, prog):
        result = self.expr.evaluate(prog)
        prog.set_result(result)

    def __repr__(self):
        return "return %s" % (self.expr)

class FunctionCall:
    def __init__(self, id, args):
        self.name = id
        self.args = args

    def evaluate(self, prog):
        vals = []
        for a in self.args:
            vals.append(a.evaluate(prog))
        return prog.call_function(self.name, vals)

    def __trunc__(self):
        sum = 0
        for arg in self.args:
            sum += arg
        return sum

    def __repr__(self):
        return "FunctionCall"


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
    'topstmt : FUNC ID PARENL optfuncargs PARENR NEWLINE code END NEWLINE'
    p[0] = FunctionDef(p[2], p[4], p[7])

def p_optfuncargs(p):
    '''optfuncargs : funcargs
            | empty'''
    p[0] = p[1]

def p_funcargs_first(p):
    'funcargs : ID'
    p[0] = [p[1]]

def p_funcargs_more(p):
    'funcargs : funcargs COMMA ID'
    p[0] = p[1]
    p[0].append(p[3])

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

def p_stmt_return(p):
    'stmt : RETURN expr'
    p[0] = ReturnStmt(p[2])


def p_empty(p):
    'empty :'
    p[0] = []

def p_expr_negation(p):
    'expr : MINUS expr'
    p[0] = - p[2]

def p_expr_parened(p):
    'expr : PARENL expr PARENR'
    p[0] = p[2]

def p_expr_functioncall(p):
    'expr : ID PARENL optcallargs PARENR'
    p[0] = FunctionCall(p[1], p[3])

def p_optcallargs(p):
    '''optcallargs : callargs
            | empty'''
    p[0] = p[1]

def p_callargs_first(p):
    'callargs : expr'
    p[0] = [p[1]]

def p_callargs_more(p):
    'callargs : callargs COMMA expr'
    p[0] = p[1]
    p[0].append(p[3])

def p_expr_plusminus(p):
    '''expr : expr PLUS expr 
            | expr MINUS expr'''
    if p[2] == '+':
        p[0] = AddExpr(p[1], p[3])
    elif p[2] == '-':
        p[0] = int(p[1]) - int(p[3])
        print "%d %s %d = %d" % (p[1], p[2], p[3], p[0])

def p_expr_times(p):
    'expr : expr TIMES expr'
    p[0] = MultExpr(p[1], p[3])

def p_expr_divide(p):
    'expr : expr DIVIDE expr'
    p[0] = p[1] / p[3]
    print "%d / %d = %d" % (p[1], p[3], p[0])

def p_expr_id(p):
    'expr : ID'
    p[0] = VarExpr(p[1])

def p_expr_number(p):
    'expr : NUMBER'
    p[0] = ConstIntExpr(p[1])

def p_error(p):
    print "parse error: %s" % str(p)


class CallFrame:
    def __init__(self, funcdef, args):
        self.name = funcdef.name
        self.code = funcdef.code
        self.args = args
        self.result = None
        self.locals = dict()

class Program:
    def __init__(self, prog):
        self.prog = prog
        self.callstack = []

    def call_function(self, fname, args):
        self._push_function(fname, args)
        result = self.run()
        self.callstack.pop(-1)
        return result

    def find_function(self, fname):
        for s in self.prog:
            if s.__class__.__name__ == 'FunctionDef':
                if s.name == fname:
                    return s
        return None

    def _push_function(self, fname, args):
        if args is None:
            args = []
        f = self.find_function(fname)
        passed_argc = len(args)
        if passed_argc != len(f.args):
            print "function arg mismatch"
            return None

        self.callstack.append(CallFrame(f, args))
        i = 0
        while i < passed_argc:
            name = f.args[i]
            val = args[i]
            self.set_local(name, val)
            i += 1

    def run(self):
        frame = self.callstack[-1]
        for i in frame.code:
            i.execute(self)
        return frame.result

    def set_result(self, value):
        self.callstack[-1].result = value

    def set_local(self, name, value):
        frame = self.callstack[-1]
        frame.locals[name] = value

    def get(self, name):
        frame = self.callstack[-1]
        if name not in frame.locals:
            print "var %s is not set in %s" % (name, frame.locals)
            return None
        return frame.locals[name]

    def print_code(self):
        for s in self.prog:
            if s.__class__.__name__ == 'FunctionDef':
                s.print_code()
            else:
                print "Unknown Statement: %s" % str(s)


data = '''
3 + if 4 * 10
  + -20 *2 <-
'''

plus_data = "sum(9,3) + 24 / ( 5 + 3 ) - f(5)"

sample1 = '''func twice(n)
    return n * 2
end

func main(tacos)
    x <- twice(tacos)
    return x + 4
end
'''


lex.lex()

cmd = 'x'
if cmd == 'x':
    parser = yacc.yacc()
    progcode = parser.parse(sample1)
    program = Program(progcode)
    print program.call_function('main', [5])
elif cmd == 'p':
    parser = yacc.yacc()
    progcode = parser.parse(sample1)
    program = Program(progcode)
    program.print_code()
else:
    lex.input(sample1)
    while True:
        tok = lex.token()
        if not tok:
            break
        print tok
