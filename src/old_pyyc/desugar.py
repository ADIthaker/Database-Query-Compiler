# import ast

# class Desugar(ast.NodeTransformer):
    
#     def visit_BoolOp(self, node):
        
#         if isinstance(node, ast.If):
#             print("Found if&&&&&&&&&&&&")
            
#         if isinstance(node.op, ast.And):
#             return ast.If(test=node.values[0], body=[ast.Expr(value=node.values[1])], orelse=[ast.Pass()])
#         elif isinstance(node.op, ast.Or):
#             print("Inside or operation")
#             return ast.If(test=node.values[0], body=[ast.Pass()], orelse=[ast.Expr(value=node.values[1])])
        
# #         elif isinstance(node.op, ast.And):
# #             new_node = ast.IfExp(test=node.values[0], body=node.values[1], orelse=ast.NameConstant(value=False))
# #             ast.copy_location(new_node, node)
# #             ast.fix_missing_locations(new_node)
# #             return new_node
        
        
# #         elif isinstance(node.op, ast.Or):
# #             print("Inside or operation")
# #             new_node = ast.IfExp(test=node.values[0], body=ast.NameConstant(value=True), orelse=node.values[1])
# #             ast.copy_location(new_node, node)
# #             ast.fix_missing_locations(new_node)
# #             return new_node
        
        
#         return self.generic_visit(node)

# expression = "y = a or b"
# expression1 = """
# x = 10
# if x == 10:
#     if x != 12:
#         print(x)
# """

# if __name__ == "__main__":
#     lst = [expression]
#     for expr in lst:
#         parsed_ast = ast.parse(expr, mode='exec')

#         print("Original AST:")
#         print(ast.dump(parsed_ast, indent=4))

#         desugar_obj = Desugar()
#         modified_ast = desugar_obj.visit(parsed_ast)
#         print("-----------------------------------------------")
#         print("\nModified AST:")
#         print(ast.dump(modified_ast, indent=4))
#         print("################################################")
















class Desugar():
    
    def __init__(self, code):
        self.code = code
        self.pre_code_list = []
        self.post_code_list = []
        self.generated_numbers = set()    
        self.counter = 0
        ...
        
    def __del__(self):
        ...
        
    def generate_id(self):
        while True:
            unique_digits = random.sample(range(10), 4)
            number = int(''.join(map(str, unique_digits)))        
            if number not in self.generated_numbers:
                self.generated_numbers.add(number)            
                return number                         
      
    # GEtting new variable name
    def get_new_var_name(self):
        name = f"t_ds_{self.generate_id()}_{self.counter}"
        self.counter += 1      
        return name
        
    def code_list(self):
        self.pre_code_list = self.code.splitlines()        
        print(self.pre_code_list)
        ...
        
    def traverse(self):
        identifiers = ['and', 'or', 'not']
        for i in self.pre_code_list:
            
            # Flat or and nots
            # while any(keyword in i for keyword in identifiers):
            #     ...            
            if any(keyword in i for keyword in identifiers):
                ast.parse()
                new_var_name = self.get_new_var_name()
                print(i)
            else:
                self.post_code_list.append(i)
        print(self.post_code_list)
        ...


expression = """
if (a or b):
    print(a)
else:
    print(b)
"""

if __name__ == "__main__":
    
    desugar = Desugar(expression)   
    desugar.code_list()
    desugar.traverse()