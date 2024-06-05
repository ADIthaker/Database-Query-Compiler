# Add shebang
import ast
from ast import *
from stack_defn import Stack
import random
import hashlib



def  print_(*prompt):
    string = [i for i in prompt]
    print(f"Flatten: {' '.join(string)}")

def done():
    print('-' * 80)
    
def generate_node_id(node):
    # Convert the node to a string representation
    node_str = ast.dump(node)
    # Generate a unique identifier using a hash function
    node_id = hashlib.md5(node_str.encode()).hexdigest()
    return node_id
        
class PostfixVisitor(ast.NodeVisitor):
    
    def __init__(self):
        self.stack = Stack()
        self.counter = 0
        self.variables = {}
        self.flatExpr = []
        self.ctx = None
        self.runtimeVar = []
        self.var_order = []
        self.var_counter = 0
        self.generated_numbers = set()
        
        # Conditional Data
        self.conditional = [None, False]
        self.conditional_effect = {}
        self.cond_id = None
        self.cond_nest_stack = Stack()
        self.while_cond_dict = {}
        self.cond_active = Stack()
        # self.while = []
        
    def __del__(self):
        # print("OOOOOOOOOOVVVVVVV", self.var_order)    
        print("\n\nCompiled Variables: ")
        
        for key in self.variables:
            print(f"{key}: {self.variables[key]}")
            
        print("\n\nRuntime Variables: ")
        string = ", ".join(str(var) for var in self.runtimeVar)
        print(string)                                
        
        print("\n\nFlat Expressions: ")
        for expr in self.flatExpr:
            print(expr)
            # return self.flatExpr
            
        # self.stack.iterate() 
        
    # ------------------------------------ CUSTOM FUNCTIONS -----------------------------------
    
    def generate_id(self):
        while True:
            unique_digits = random.sample(range(10), 4)
            number = int(''.join(map(str, unique_digits)))        
            if number not in self.generated_numbers:
                self.generated_numbers.add(number)            
                return number
    
    # Get value type and value
    def process_constants(self, arr = None):
        if arr is None:
            arr = self.stack
        val_type = arr.pop()
        val = arr.pop()
        return val_type, val                  
      
    # GEtting new variable name
    def get_new_var_name(self):
        name = f"t_{self.generate_id()}_{self.counter}"

        self.counter += 1      
        return name
     
    # Storing variable order
    def __store_var_order__(self, var_name):
        self.var_order.append(var_name)
        
    # return variable order
    def _return_var_order_(self):
        return self.var_order
    
    # String constant variables to dicts
    def store_constant_var(self, var_name, value):
        self.variables[var_name] = value
        self.__store_var_order__(var_name)
    
    # Storing runtime variables to list
    def store_runtime_var(self, var_name):
        self.runtimeVar.append(var_name)
        self.__store_var_order__(var_name)    
        
    def stack_push(self, *args):
        for i in args:
            self.stack.push(i)
    
    def set_active_conditional(self, Condition = None, Bool = False, Node_id = None):
        self.conditional = [Condition, Bool, Node_id]
        if Condition != None and Bool != None and Node_id != None:
            self.cond_id = f"{Condition}_{Node_id}"            
            self.cond_active.push(self.cond_id)
            # print(self.conditional)
        else:
            node_id = self.cond_active.pop()
    
    def set_conditional(self, Condition = None, Bool = False, Node_id = None, set_Active = True, *args):
        self.conditional = [Condition, Bool, Node_id]
        
        # If some args are passed
        for i in args:
            self.conditional.append(i)
            
        # Actual check if we get something from if, ifexp, while
        if Condition != None and Bool != None and Node_id != None:
            self.cond_id = f"{Condition}_{Node_id}"            
            self.cond_nest_stack.push(self.cond_id)
            if set_Active == True:
                self.set_active_conditional(Condition, Bool, Node_id)
            # print(self.conditional)
        else:
            node_id = self.cond_nest_stack.pop()
            if set_Active == True:
                self.set_active_conditional()
            
        
    def add_flat_expr(self, args, isConditional = False, Size = False, addIndent = True, tab_length = None):            
        tab_space_length = (self.cond_active.size()) if isConditional == False else (self.cond_active.size() - 1)           
        
        if Size == True:
            print(self.cond_active.size(), tab_space_length)
        
        if addIndent == False:
            tab_space_length = 0
        
        if tab_length != None:
            tab_space_length = tab_length
        
        for i in args:
            # print(tab_space, "...............")
            self.flatExpr.append("{}{}".format(tab_space_length * '\t', i))
    
    
    def get_flat_expr(self):
        return self.flatExpr
        
    # ----------------------------------------------------------
    
    def process_if_test_body(self, node):    
        string = "" 
        if isinstance(node, ast.If):
            string = "If"
        elif isinstance(node, ast.IfExp): 
            string = "IfExp"

        # Process the 'if' condition
        # print("@@@@@@@@@@@ Inside If")               
        if string == "IfExp":
            new_var_name = self.get_new_var_name()     
            self.store_runtime_var(new_var_name)
            self.add_flat_expr([f"{new_var_name} = 0"])
            
        self.traverse(node.test)        
        self.set_conditional(string, True, generate_node_id(node))
        self.addFlatCode(string)            

        # print("@@@@@@@@@@@ Processing if body")
        # Process the 'if' body
        # print(ast.dump(node.body))
        if isinstance(node.body, list):
            for stmt in node.body:
                self.traverse(stmt)
        else:
            self.traverse(node.body)
            # Call ifexp func                    
            self.addFlatCode('IfExp_body', [new_var_name])

        # print("@@@@@@@@@@@ Done Processing")
        # Update information about the last traversal            
        self.set_conditional()
            
    def process_orelse(self, node, isIfExp = False):
        # print("@@@@@@@@@@@ Starting orelse")            
        self.set_conditional("Else", True, generate_node_id(node))        
        if isIfExp or len(node.orelse) > 0:
            self.add_flat_expr([f"else:"], True)
            
        if isinstance(node.orelse, list):
            for stmt in node.orelse:
                self.traverse(stmt)
        else:
            self.traverse(node.orelse)
            self.addFlatCode("IfExp_orelse")
            
        self.set_conditional()
        # print("@@@@@@@@@@@ Done orelse")
        
        
#     def process_while_test_body(self, node):        
#         # Process the 'if' condition
#         print("@@@@@@@@@@@ Beginning While")
        
#         print("@@@@@@@@@@@ Processing While Test")
#         while_call = False
#         if isinstance(node.test, Call):
#             while_call = True
#         self.traverse(node.test)
#         #
#         self.set_conditional("While", True, generate_node_id(node))
        
#         if while_call:
#             condition_repeat = self.flatExpr[-1]
#             # print(condition_repeat)
#         self.addFlatCode("While")            

#         print("@@@@@@@@@@@ Processing While body")
#         # Process the 'if' body
#         for stmt in node.body:
#             self.traverse(stmt)

#         # print("@@@@@@@@@@@ Done Processing")
#         # Update information about the last traversal  
#         if while_call:
#             print("@@@@@@@@@@@ Appending while")       
#             print(condition_repeat)
#             self.add_flat_expr([condition_repeat.strip()], Size=True)
#             print("@@@@@@@@@@@ Done Appending")
#         while_call = False
#         self.set_conditional()
#         print("@@@@@@@@@@@ Ending While")


    def process_while_test_body(self, node):        
        # Process the 'if' condition
        print("@@@@@@@@@@@ Beginning While")
        
        id_ = generate_node_id(node)
        active_cond = True
        if isinstance(node.test, Compare):
            self.set_conditional("While", True, id_)
            
        else:
            self.set_conditional("While", True, id_, set_Active = False)
            active_cond = False
        print("$$$Appended")
        
        print("@@@ Processing While Test")
        print("@@@ Processing While Test", ast.dump(node.test))                
                
        # print(len(self.flatExpr))
        num = len(self.flatExpr)
        tab_length = self.cond_active.size()
        self.traverse(node.test)
        cond = []
        # print(len(self.flatExpr))
        for i in range(num, len(self.flatExpr)):
            # print("|||||||||||", self.flatExpr[i])
            cond.append(self.flatExpr[i])
        
        if active_cond != True:
            self.set_active_conditional("While", True, id_)
        # Laying groundwork                
        self.addFlatCode("While")            

        print("@@@ Processing While body")        
        for stmt in node.body:
            self.traverse(stmt)

        # if id_ in self.while_cond_dict:
        #     string = self.while_cond_dict.pop(id_)
        #     self.add_flat_expr([string]) 
        final_length = self.cond_active.size() - tab_length
        self.add_flat_expr(cond, tab_length = final_length)
        self.set_conditional()
        print("@@@@@@@@@@@ Ending While")

    # ----------------------------------------------------------
        
    def traverse(self, node):
        
        # Visits if test and if body
        if isinstance(node, ast.If) or isinstance(node, ast.IfExp):
            self.process_if_test_body(node)
        
        # Visits while test and while body
        if isinstance(node, ast.While):
            self.process_while_test_body(node)
        
        # Traverse left subtree first and then the right        
        for child in ast.iter_child_nodes(node):
            if not isinstance(node, ast.If) and not isinstance(node, ast.IfExp) and not isinstance(node, ast.While):
                self.traverse(child)
        
        # Process the 'else' block, if present
        if isinstance(node, ast.If) or isinstance(node, ast.IfExp):
            res = False
            if isinstance(node, ast.IfExp):
                res = True
            self.process_orelse(node, isIfExp = res)
        else:
            self.visit(node)
        
        
    # --------------------------------------------------------------------------

    def visit(self, node):  
        # Check if a node value push it to stack
        # print(f"\n{self.counter}: ")
        
        try:
            if (node.value == 0 or node.value) and type(node.value) is int:
                # print(f"Value: {node.value}")                
                self.stack_push(node.value)                
        except:
            ...
            
        # Check if node id like 'print' and push to stack
        try:
            if node.id:
                avoid_list = ["eval", "input", "int"]
                # print(f"Id: {node.id}")
                if node.id not in avoid_list:
                    self.stack_push(node.id)
        except:
            ...
        
        # It should be an object if not value or id 
        # check the type of operation        
        self.stack_loader(node)        
    
    # -----------------------------------------------------------------------
    
    def stack_loader(self, node):
        name_type = type(node).__name__
        # print(f"Visited {name_type}")                
        arr = ['Compare', 'If', 'IfExp', 'UnaryOp', 'BinOp', 'Assign', 'Expr', 'While']
        if name_type == "Name":            
                            
            if node.id and node.id == "eval":
              # Create new var_name
              new_var_name = self.get_new_var_name()                                          
              
              # Append to runtime variables list
              self.store_runtime_var(new_var_name)
              
              # Append to flat expression
              self.add_flat_expr([f"{new_var_name} = eval(input())"])
              
              # Push the new variable and its type to stack 
              self.stack_push(new_var_name, "Constant_Variable")
            
            elif node.id and node.id == "int":            
                ...
                
            elif node.id and (node.id == "input"):
                ...  
                            
            
            elif self.ctx == "Load" and self.ctx is not None and self.stack.top() != "print":                                
                self.stack_push("Constant_Variable")
        
        elif name_type == "Store":
            self.ctx = "Store"
            self.stack_push(name_type)
            
        elif name_type == "Load":
            self.ctx = "Load"
            # self.stack_push(name_type)
        
        elif name_type == "UnaryOp":
            self.var_creator(name_type, node)
        
        elif name_type == "BoolOp":
            self.var_creator(name_type, node)  
            
        elif name_type == "Call":
            self.var_creator(name_type, node)  
        
        elif name_type == "If":
            # print("................Var_creator: If")
            self.var_creator(name_type)  
            
        elif name_type in arr:
            self.var_creator(name_type)
        else:
            self.stack_push(name_type)
        self.stack.iterate()
        
    # -----------------------------------------------------------------------         
        
    def var_creator(self, cmd, node = None):
                      
        if cmd == 'UnaryOp':
            
            
            # Can be constant or const_var
            val_type, val = self.process_constants()            
            op = self.stack.pop()            
            self.stack.iterate()
            
            if op == "USub":
                new_var_name = None                
                expr = ""
                # Some constant
                if val_type == "Constant":                    
                    # First assign value to temp_var
                    temp_var = self.get_new_var_name()
                    self.store_constant_var(temp_var, val)
                    self.add_flat_expr([f"{temp_var} = {val}"])

                    # Secondy, assign new_var_name with negation of temp_var
                    new_var_name = self.get_new_var_name()
                    self.store_constant_var(new_var_name, -val)
                    expr = f"{new_var_name} = -{temp_var}"
                    # Process on Usub

                # Variable has no previous operation of the eval input type
                elif val_type == "Constant_Variable":
                    var_name = val
                    if var_name not in self.runtimeVar:
                        val = self.variables[var_name]                   
                        new_var_name = self.get_new_var_name()
                        self.store_constant_var(new_var_name, val)
                        expr = f"{new_var_name} = -{var_name}"
                        # Process on Usub              

                    elif var_name in self.runtimeVar:                       
                        new_var_name = self.get_new_var_name()
                        self.store_runtime_var(new_var_name)
                        expr = f"{new_var_name} = -{var_name}"
                self.stack_push(new_var_name, "Constant_Variable")
                self.add_flat_expr([expr])        
                    
                    
            elif op == "Not":
                new_var_name = self.get_new_var_name()
                store_val = 0
                if val_type == "Constant":
                    if val != 0:
                        store_val = 1
                
                self.add_flat_expr([f"{new_var_name} = 0"])            
                
                new_var_name_1 = self.get_new_var_name()
                self.store_constant_var(new_var_name_1, store_val)
                
                new_var_name_2 = self.get_new_var_name()                
                self.add_flat_expr([f"{new_var_name_2} = {val}"])
                self.store_constant_var(new_var_name_2, val)
                
                self.add_flat_expr([f"{new_var_name_1} = int(0 != {new_var_name_2})"])
                self.set_conditional("If", True, generate_node_id(node))
                self.add_flat_expr([f"if {new_var_name_1}:"], True)
                self.add_flat_expr([f"{new_var_name} = 0"])
                self.set_conditional()
                                
                
                self.set_conditional("Else", True, generate_node_id(node))
                self.add_flat_expr([f"else:"], True)
                self.add_flat_expr([f"{new_var_name} = 1"])
                self.set_conditional()
                
                self.stack_push(new_var_name, "Constant_Variable")
                self.store_constant_var(new_var_name, store_val)
                ...
                
        elif cmd == 'BoolOp':
            # Push all variables to stack for l-r order
            bool_op_stack = Stack()            
            for i in range(len(node.values)):
                val_type, val = self.process_constants()
                if val_type == 'Constant':
                    new_var_name = self.get_new_var_name()
                    self.add_flat_expr([f'{new_var_name} = {val}'])
                    self.store_constant_var(new_var_name, val)
                    val = new_var_name
                    val_type = 'Constant_Variable'
                bool_op_stack.push(val)
                bool_op_stack.push(val_type)
                        
            op = self.stack.pop()
            
            if op == "Or":
                new_var_name = self.get_new_var_name()
                self.add_flat_expr([f"{new_var_name} = 0"])
                self.addFlatCode("Or", [bool_op_stack, new_var_name, node])
                self.stack_push(new_var_name, "Boolean_Constant")
                
            elif op == "And":
                new_var_name = self.get_new_var_name()
                # print("................", new_var_name)
                self.add_flat_expr([f"{new_var_name} = 0"])
                self.addFlatCode("And", [bool_op_stack, new_var_name, node])
                self.stack_push(new_var_name, "Boolean_Constant")
                ...
            
            
        
        elif cmd == 'BinOp':
            lst_value = []
            eqn = []
            op = ""
            
            if self.stack.top() == "Constant":
                r_type, r_val = self.process_constants()                
                lst_value.append(r_val)
                eqn.append(r_val)
                
                op = self.stack.pop()
                
                if self.stack.top() == "Constant":      
                    l_type, l_val = self.process_constants()                       
                    lst_value.append(l_val)    
                    eqn.append(l_val)                   
                
                elif self.stack.top() == "Constant_Variable":
                    l_type, l_var_name = self.process_constants()
                    if l_var_name not in self.runtimeVar:
                        lst_value.append(self.variables[l_var_name])
                    eqn.append(l_var_name)
                
            elif self.stack.top() == "Constant_Variable":
                r_type, r_var_name = self.process_constants()
                if r_var_name not in self.runtimeVar:
                    lst_value.append(self.variables[r_var_name])
                eqn.append(r_var_name)
                # print("first |||", lst_value)
                
                op = self.stack.pop()
                
                if self.stack.top() == "Constant":      
                    l_type, l_val = self.process_constants()     
                    lst_value.append(l_val)    
                    eqn.append(l_val)                 
                
                elif self.stack.top() == "Constant_Variable":
                    l_type, l_var_name = self.process_constants()
                    # print("second |||", l_var_name)
                    if l_var_name not in self.runtimeVar:
                        lst_value.append(self.variables[l_var_name])
                    eqn.append(l_var_name)
                    
            if op == "Add":
                # For evaluating:                
                # New variable name:
                new_var_name = self.get_new_var_name()                
                
                # Append to dict of variables
                if len(lst_value) > 1:
                    self.store_constant_var(new_var_name, sum(lst_value))                    
                
                # Append variable to stack
                self.stack_push(new_var_name, "Constant_Variable")
                
                #Create a print stmt and append to flat
                string = f"{new_var_name} = {eqn[1]} + {eqn[0]}"                            
                if any(element in eqn for element in self.runtimeVar):
                    self.store_runtime_var(new_var_name)
                self.add_flat_expr([string])
              
            
        elif cmd == 'Compare':
            # Comparing Eq
            string = ""
            new_var_name = ""
            new_var_type = ""
            val1_type, val1 = self.process_constants()                        
            op = self.stack.pop()
            
            is_there_a_parcel = False
            hash_val = ""
            id_ = ""
            print("$$$$$Searching")
            if self.cond_nest_stack.is_empty() == False:                
                hash_val = self.cond_nest_stack.top()
                print("************Hash_val", hash_val.split("_"))
                func_, id_ = hash_val.split("_")
                print(func_, id_)
                if func_ == "While":
                    is_there_a_parcel = True
            
            if op == 'Eq':                
                val2_type, val2 = self.process_constants()                
                is_Bool_runtime = False                
                new_var_name = self.get_new_var_name()
                
                # Check if any of them is in runtime var
                if val1 in self.runtimeVar or val2 in self.runtimeVar:
                    is_Bool_runtime = True
                    self.store_runtime_var(new_var_name)
                    new_var_type = "Boolean_Runtime"
                    string = f"{new_var_name} = int({val1} == {val2})"
                    
                else:
                    if val1 == val2:
                        self.store_constant_var(new_var_name, 1)
                    else:
                        self.store_constant_var(new_var_name, 0)
                    new_var_name_left = self.get_new_var_name()
                    self.add_flat_expr([f"{new_var_name_left} = {val1}"])
                    self.store_constant_var(new_var_name_left, val1)
                    string = f"{new_var_name} = int({new_var_name_left} == {val2})"
                    new_var_type = "Boolean_Constant"
                    
            elif op == 'NotEq':                
                val2_type, val2 = self.process_constants()                
                is_Bool_runtime = False                
                new_var_name = self.get_new_var_name()
                
                # Check if any of them is in runtime var
                if val1 in self.runtimeVar or val2 in self.runtimeVar:
                    is_Bool_runtime = True
                    self.store_runtime_var(new_var_name)                    
                    new_var_type = "Boolean_Runtime"
                    string = f"{new_var_name} = int({val1} != {val2})"
                    
                else:
                    if val1 != val2:
                        self.store_constant_var(new_var_name, 1)
                    else:
                        self.store_constant_var(new_var_name, 0)
                    new_var_name_left = self.get_new_var_name()
                    self.add_flat_expr([f"{new_var_name_left} = {val1}"])
                    self.store_constant_var(new_var_name_left, val1)
                    string = f"{new_var_name} = int({new_var_name_left} != {val2})"
                    new_var_type = "Boolean_Constant"
                    
            self.add_flat_expr([string])            
            if is_there_a_parcel == True:
                print("$$$$$$$Pushing into stack")
                self.while_cond_dict[id_] = string
            self.stack_push(new_var_name, new_var_type)
                                    
        elif cmd == 'Call':                            
            ...
            
        elif cmd == 'Assign':
            # print(".........Assigning")
            val_type = self.stack.pop()
            val = self.stack.pop()
            var_name = self.stack.pop()
            if self.stack.pop() == 'Store':
                
                if val_type == "Constant_Variable" and val not in self.runtimeVar:
                    # self.stack.iterate()
                    temp = self.variables[val]
                    # print("????????", temp, type(temp))
                    while not isinstance(temp, int):
                        temp = self.variables[temp]

                    self.store_constant_var(var_name, temp)  
                    
                elif val_type == "Constant_Variable" and val in self.runtimeVar:
                    self.store_runtime_var(var_name)
                    
                elif val_type == "Constant":                    
                    self.store_constant_var(var_name, val)
                    
                elif val_type == "Boolean_Constant":                    
                    self.store_constant_var(var_name, val)
                
                # self.stack_push(var_name, "Constant_Variable")
                # self.stack.iterate()
                
                self.add_flat_expr([f"{var_name} = {val}"])                 
                # done()
                
        elif cmd == 'Expr':
            # self.stack.iterate()
            val_type, val = None, None
            val_type, val = self.process_constants()     
            if val_type == "Constant":
                       
                # print("{{{{{{Inside Constant")
                # print(f"{val_type}: {val}")
                # Get a variable name
                new_var_name = self.get_new_var_name()
                
                # Push variable value to dictionary
                self.store_constant_var(new_var_name, val)
                
                # Push variable expression to flat_expr
                self.add_flat_expr([f"{new_var_name} = {val}"])
                # Push var name and type to stack                
                self.stack_push(new_var_name, "Constant_Variable")                
                # Call this function again
                # print("Calling Expr")
                # self.stack.iterate()
                self.var_creator("Expr")                
                        
            
            elif self.stack.size() > 0 and self.stack.top() == "print":                
                op = self.stack.pop()
                
                if self.stack.is_empty() is False \
                and self.conditional[1] == False:
                    self.add_flat_expr([f"print({val})"])
                    
                if val and val_type and op == "print":
                    self.add_flat_expr([f"print({val})"])

                elif self.conditional[0] == "If" or self.conditional[0] == "Else":
                    self.add_flat_expr([f"print({val})"])
                    ...             

                    
# -----------------------------------------------------------                    
    def addFlatCode(self, cmd, bool_op = None):
        
        if cmd == "If" or cmd == "IfExp":                        
                
            # bool_type, bool_val = self.process_constants()           
            cond_type, cond_val = self.process_constants()                 
            self.add_flat_expr([f"if {cond_val}:"], True)
                        
        elif cmd == "IfExp_body":
            assign_type, assign = self.process_constants()
            new_var_name = bool_op[0]
            self.stack_push(new_var_name, "Constant_Variable")
            self.add_flat_expr([f"{new_var_name} = {assign}"])
            
        elif cmd == "IfExp_orelse":
            assign_type, assign = self.process_constants()
            var_type, var_name = self.process_constants()
            self.stack_push(var_name, var_type)            
            self.add_flat_expr([f"{var_name} = {assign}"])
            
        elif cmd == "While":
            cond_type, cond_val = self.process_constants()            
            self.add_flat_expr([f"while {cond_val}:"], True)
            ...
            
        elif cmd == "Or":
            bool_op_stack, new_var_name, node = bool_op
            if (bool_op_stack.size() > 2):                
                self.set_conditional("If", True, generate_node_id(node))
                val_type = bool_op_stack.pop()
                val = bool_op_stack.pop()                
                self.add_flat_expr([f"if {val}:"], True)
                self.add_flat_expr([f"{new_var_name} = {val}"])
                self.set_conditional()
                
                self.set_conditional("Else", True, generate_node_id(node))
                self.add_flat_expr([f"else:"], True)                
                self.addFlatCode("Or", [bool_op_stack, new_var_name, node])
                self.set_conditional()
            elif bool_op_stack.size() == 2:
                val_type = bool_op_stack.pop()
                val = bool_op_stack.pop()                
                self.add_flat_expr([f"{new_var_name} = {val}"])
                
                
        elif cmd == "And":
            bool_op_stack, new_var_name, node = bool_op
            
            if (bool_op_stack.size() > 2):
                
                self.set_conditional("If", True, generate_node_id(node))
                val_type = bool_op_stack.pop()
                val = bool_op_stack.pop()                
                self.add_flat_expr([f"if {val}:"], True)
                
                self.addFlatCode("And", [bool_op_stack, new_var_name, node])                                
                
                self.set_conditional()
                
                self.set_conditional("Else", True, generate_node_id(node))
                self.add_flat_expr([f"else:"], True) 
                self.add_flat_expr([f"{new_var_name} = 0"])   
                self.set_conditional()
                
            elif (bool_op_stack.size() == 2):
                
                val_type = bool_op_stack.pop()
                val = bool_op_stack.pop()        
                
                self.set_conditional("If", True, generate_node_id(node))
                self.add_flat_expr([f"if {val}:"], True)
                self.add_flat_expr([f"{new_var_name} = {val}"])
                self.set_conditional()
                
                self.set_conditional("Else", True, generate_node_id(node))
                self.add_flat_expr([f"else:"], True) 
                self.add_flat_expr([f"{new_var_name} = 0"])   
                self.set_conditional()
            
                
            ...

            
if  __name__ == "__main__":
    expression ="""
x = 5
y = 10
"""
    expression1 = """
x = 5
if int(x == 23 or x == 5):
    x  = x + 10    
    print(x)
    """
    
    expression2 = """
x = 0
if int(x == 5):
    print(x)    
    """
    
    expression3 = """
x = 0
while(int(x) != 20):
    print(x)
    x = x + 1
    """
    
    expression3 = """
x = 0
while(int(x) != 20):
    if x == 10:
        print(10)
    else:
        print(2)
    print(x)
    x = x + 1
    """
    
    expression4 = """
x = 5
y = 10
if int(eval(input()) == 23):
    print(y+x)
else:
    print(y+-x)
    """
    
    expression5 = """
y = a or b and c
    """
    
    expression5 = """
y = a or b
    """        
    
    expression6 = """
y = 10 if (x == 0) else 0

    """
    
    expression6 = """
# r = q if (x if y else z) else (a if int(b==3) else c)
x = 0
if int(x == 5):
    print(x)
     """
    
    
    expression6 = """
a = 23
print(a + 34)
if x:
    print(a + 3)
else:
    print(a - 3)
    """
    
    
    expression6 = """
a = 2
x = 5
while x:
    print(x)
    while a:
        print(a)
        
while(a):
    print(a)    
    """
    expression6 = """
x = eval(input())
a = 10
while (int(x != 23)):
    print(42)
    x = x + 1
    while a:
        print(a)
"""    
    
    expression6 = """
if 10:
    print(x)
"""    

    expression6 = """
x = 3
y = 0
while x != 0:    
    while y != 2:
        print(y)
        y = y + 1    
    print(x)
    x = x + - 1
"""
    
#     expression6 = """
# x = 3
# while x:
#     print(x)
#     x = x + - 1
# """

#     expression6 = """
# while (eval(input())):
#     print(1)
# """


    expression6 = """
print(int(not int(not 0)) + 1)
    """
    
    expression6 = """
x = 1
y = 2
z = 0
loop_condition = 1

while int(x != 5):
    if (int(x == 1) or int(x == 4)):
        if int(y == 2):
            z = z + 1
        else:
            if int(y == 1):
                z = z + 2
            else:
                z = z + 3
    else:
        if (int(x == 2) or int(x == 5)):
            if int(y == 2):
                z = z + 2
            else:
                if int(y == 1):
                    z = z + 3
                else:
                    z = z + 1
        else:
            if int(y == 2):
                z = z + 3
            else:
                if int(y == 1):
                    z = z + 1
                else:
                    z = z + 2
            
    x = x + 1
    y = y + -1
    
print(z)


    """
    
    expression6 = """
print(int(not int(not 0)) + 1)
    """


         
    tree = ast.parse(expression6)    
    print(ast.dump(tree, indent = 4))
    postfix_visitor = PostfixVisitor()
    postfix_visitor.traverse(tree)