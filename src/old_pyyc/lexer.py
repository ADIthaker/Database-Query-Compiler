tokens = ('PRINT', 'INT', 'LPAR', 'RPAR', 'EVAL', 'INPUT', 'PLUS', 'MINUS', 'WS', 'EQUAL', 'VAR')

t_PRINT = r'print'
t_PLUS = r'\+'
t_LPAR = r'\('
t_RPAR = r'\)'
t_MINUS = r'\-'
t_EVAL = r'eval'
t_INPUT = r'input'
t_EQUAL = r'='
t_VAR = r'\w+'
t_ignore_WS = r'\ '
t_ignore_COMMENT = r'\#.*'


def t_INT(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large", t.value)
    return t


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

import ply.lex as lex

lexer = lex.lex()
code = '''print(-eval(input()) + 2 + 5)'''
lexer.input(code)

while True:
    tok = lexer.token()    
    if not tok:
        break      # No more input
    # print(tok)