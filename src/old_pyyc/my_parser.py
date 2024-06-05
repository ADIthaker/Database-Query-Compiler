import ast
from ast import *

from lexer import tokens


precedence = (
    ('left', 'PLUS', 'MINUS'),
)

# def p_program_module(t):
#     "program: module"
#     t[0] = 
        
def p_module_statement(t):
    "module : statements"
    t[0] = Module(t[1])
    
def p_empty(t):
    'empty :'
    pass

def p_module_empty(t):
    'module : empty'
    t[0] = Module([])
    
def p_block_statement(t):
    '''statements : statement
                 | statements statement'''
    if len(t) == 2:
        t[0] = [t[1]]
    else:
        t[1].append(t[2])
        t[0] = t[1]

def p_statement_expression(t):
    "statement : expression"
    t[0] = Expr(value=t[1])

def p_print_statement(t):
    'statement : PRINT LPAR expression RPAR'
    t[0] = Expr(Call(Name("print", Load()), [t[3]], []))

def p_statement_assignment(t):
    "statement : VAR EQUAL expression"
    t[0] = Assign([Name(t[1], Store())], t[3], [])
    
def p_par_expression(t):
    "expression : LPAR expression RPAR"
    t[0] = t[2]

def p_expression_var(t):
    "expression : VAR"
    t[0] = Name(t[1], Load())

def p_minus_expr(t):
    "expression : MINUS expression"
    t[0] = UnaryOp(USub(), t[2])    
    
def p_eval_input_statement(t):
    'expression : EVAL LPAR INPUT LPAR RPAR RPAR'
    t[0] = Call(Name(id='eval', ctx=Load()),[Call(Name(id='input', ctx=Load()),)])
    
def p_add_statement(t):
    'expression : expression PLUS expression'
    t[0] = BinOp(t[1], Add(), t[3])
    
def p_expression_int(t):
    'expression : INT'
    t[0] = Constant(t[1])
    
def p_error(t):
    print("Syntax error '%s'" %t.value)
    # try:
        # if t.value:
        #     print("Syntax error '%s'" %t.value)
        # except err:
        #     print()
        # finally:
        #     print("Empty Python String")
    
import ply.yacc as yacc

def parse_code(inp):
    parser = yacc.yacc()
    result = parser.parse(inp)
    return result
    
if __name__ == "__main__":
    s = '''
print(x)
x = x+5
#bruh
'''
    result = parse_code(s)
    # result = parser.parse(s) 
    # print("Above result")
    # print(result) # an AST for P0
    print(ast.dump(result, indent=2))