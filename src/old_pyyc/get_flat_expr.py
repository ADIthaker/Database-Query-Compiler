import ast
from ast import *
from flatten import PostfixVisitor
#from my_parser import parse_code

class Flat_Expr:
    def __init__(self, file_dir):
        self.file_dir = file_dir
        self.string_code_lst = []
        self.flat_expr = []
        self.flat_var_order = []
        ...
    
    def print_actual_ast(self):
        # print("Printing AST before Flattening")
        prog = ""
        with open(f"{self.file_dir}", 'r') as file:
        # Open the file and read     
            prog = file.read()
        # print(ast.dump(ast.parse(prog), indent=2))
        
    def get_string_code(self):                
        string = ""
        with open(f"{self.file_dir}", 'r') as file:
            self.code = file.read()
        # Open the file and read     
            for line in file:        
                line = line.rstrip()
                # Remove empty blank spaced strings
                if line != "":            
                    self.string_code_lst.append(line)
        # print(self.string_code_lst)
        print("Code Reading: Success")        
        
    def convert_to_flat(self):
        # Form a combined expression separated by \n
        expression = self.code#"\n".join(str(expr) for expr in self.string_code_lst)
        # expression = "\n".join(str(expr) for expr in self.string_code_lst)        
        # Parse the tree
        tree = ast.parse(expression)
        # print("#################################Actual Tree is: ", ast.dump(tree, indent = 4))
        print(expression)
        tree = ast.parse(expression) #parse_code(expression)
        # tree = parse_code(expression)
        # print("#################################My Tree is: ", ast.dump(tree, indent = 4))
        
        # Flat the tree
        postfix_visitor = PostfixVisitor()
        postfix_visitor.traverse(tree)

        # Get the Flat Expr list, var occurence order
        self.flat_expr = postfix_visitor.get_flat_expr()
        self.flat_var_order = postfix_visitor._return_var_order_()
        # print("Flat Expression:", self.flat_expr)
        print("Flat_Expr: Code Flattening: Success")
        return {"flat_list": self.flat_expr, "var_order": self.flat_var_order}