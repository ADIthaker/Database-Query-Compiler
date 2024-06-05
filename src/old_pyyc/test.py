import ast
from ast import *

expression1 = """
a = 2
if a == 1:
    print(a)
"""

expression2 = """
a = 2
while a:
    x = x + 1
print(a)
"""

expression3 = """
if y:
    t0 = x
else:
    t0 = z
if t0:
    r = q
else:
    t1 = int(b==3)
    if t1:
        r = a
    else:
        r = c
"""



tree = ast.parse(expression3)
print(ast.dump(tree, indent = 4))