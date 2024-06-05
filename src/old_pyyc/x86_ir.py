import ast
from ast import *
from stack_defn import Stack
import random
import networkx as nx



class X86_IR():
    
    def __init__(self, module):
        self.module = module
        self.stack = Stack()
        self.IR = []
        self.if_count = 0
        
    def __del__(self):
        self.stack.iterate()
        for i in self.IR:
            print(i)
        
    def stack_push(self, *args):
        for i in args:
            self.stack.push(i)
            
    def IR_append(self, *args):
        lst = []
        for i in args:
            lst.append(i)
            
        self.IR.append(lst)
        
    def dump(self, obj):
        string = ast.dump(obj)[:-2]
        return string
            
    def process_consts(self):
        return self.stack.pop(), self.stack.pop()
    
    def track_IR_instance(self, st_node):
        self.stack.iterate()
        
        if isinstance(st_node, Constant):
            val = st_node.value
            self.stack_push(val, "Constant")
        
        # elif isinstance(st_node, ops):
            
        
        elif isinstance(st_node, Name):            
            id = st_node.id
            ctx = st_node.ctx            
            # print('%%%%%%%', id, self.dump(ctx))
            # id='int', ctx=Load()
            if id != 'int':
                self.stack_push(id, self.dump(ctx))
            
        elif isinstance(st_node, Assign):
            tar = st_node.targets[0]
            self.track_IR_instance(tar)
            val = st_node.value
            self.track_IR_instance(val)
            
            left_type, left_val = self.process_consts()
            right_type, right_val = self.process_consts()
            self.IR_append('movl', left_val, right_val)
        
#         elif isinstance(st_node, UnaryOp):
#             op = self.dump(st_node.op)
            
#             if op == "USub":
#                 operand 
        
        elif isinstance(st_node, Expr):
            val = st_node.value
            self.track_IR_instance(val)
            val1_type, val1 = self.process_consts()
            func_type, func = self.process_consts()
            if func == 'print':
                self.IR_append('call', 'print_int_nl', val1)
        
        elif isinstance(st_node, Call):
            func = st_node.func
            self.track_IR_instance(func)
            
            for node in st_node.args:
                self.track_IR_instance(node)            
                
        elif isinstance(st_node, Compare):
            left = st_node.left
            self.track_IR_instance(left)
            for op in st_node.ops:
                # print(self.dump(op))
                op = self.dump(op)
                self.track_IR_instance(op)
            for comp in st_node.comparators:
                print(self.dump(comp))
                self.track_IR_instance(comp)            
                
            if op == 'NotEq':
                c1_type, c1 = self.process_consts()
                c2_type, c2 = self.process_consts()                
                self.IR_append('cmpl', c1, c2)
                self.IR_append('setne', 'al')     
                self.stack_push('al', 'Register')
                
            elif op == 'Eq':
                c1_type, c1 = self.process_consts()
                c2_type, c2 = self.process_consts()                
                self.IR_append('cmpl', c1, c2)
                self.IR_append('sete', 'al')    
                self.stack_push('al', 'Register')
                
        
        elif isinstance(st_node, If):
            num = self.if_count
            test = st_node.test
            self.track_IR_instance(test)
            if_type, if_val = self.process_consts()
            self.IR_append('cmpl', 0, if_val)
            if len(st_node.orelse) > 0:
                self.IR_append('je', f'else{num}')
                        
            self.IR_append(f'then{num}:')
            for body in st_node.body:                
                self.track_IR_instance(body)
            self.IR_append('jmp', f'end{num}')
                
            if len(st_node.orelse) > 0:
                self.IR_append(f'else{num}:')
            for orelse in st_node.orelse:
                self.track_IR_instance(orelse)
            self.IR_append(f'end{num}:')
            self.if_count += 1
                
            
            
                
            
                
        
            
        ...
            
        
    def traverse(self):
        for i in self.module:
            print(ast.dump(i), end = "\n\n---------------------\n")
        
        for i in range(len(self.module)):
            self.track_IR_instance(self.module[i])          