import sys
from get_flat_expr import Flat_Expr
import ast
from ast import *
from assembly import Assembler
import os
from x86_starter import base_starter_template
from register_allocation import Register_Allocation
# ./pyyc mytests/test1.py

def print_(prompt):
    print(f"Compile: {prompt}")

class Compile_P0:
    # pass sys.argv[1] to get_flat_
    def __init__(self):
        
        self.final_assembly = ""
        
        # Get file name from pyyc cmd
        self.file_dir = sys.argv[1]        
        self.raw_file_name = self.file_dir.split("/")[-1].split(".")[0]              
        
        ## create_assembly_IR
        self.assembler = None
        self.IR, self.liveness, self.graph = None, None, None
        
        ## assign_registers
        self.allocated_var = None        
        self.stack_var = {}
        self.iteration = 0
        self.unspillable = []
        
        # Creating a object for getting flat expression
        flat_obj = Flat_Expr(self.file_dir)        
        flat_obj.get_string_code()
        
        flat = flat_obj.convert_to_flat()
        self.flat_expr = flat['flat_list']
        self.var_order = flat['var_order']
        # print("VVVVVOOOOOOO", self.var_order)
        flattened_code = "\n".join(self.flat_expr)        
        print("Flattened Code")
        print(flattened_code)
        
        self.flat_ast = ast.parse(flattened_code) 
        # print("Flat AST")
        # print(ast.dump(self.flat_ast))
        self.total_var = len(self.var_order)               
        self.starter_template, self.ending_template = base_starter_template(self.total_var)         
        print_("Getting Flat Code: Success")
    
    def create_assembly_IR(self):
        # print(ast.dump(self.flat_ast))
        self.assembler = Assembler(self.var_order, self.flat_ast)
        
        # print(self.var_order)
        self.IR, self.liveness, self.graph = self.assembler.get_assembly_IR()
        print("liveness, graph done")

    
    def __addl_temp_for_stack__(self, i, local_iteration):
        addFrom = i[1]
        addTo = i[2]
        var_name = f"t_us_{self.iteration}_{local_iteration}"
        var_reg = '%esi'
        i1 = ["movl", f"{addFrom}", var_reg]
        i2 = ["addl", var_reg, f"{addTo}"]        
        return [i1, i2]  
        
    def __movl_temp_for_stack__(self, i, local_iteration):
        moveFrom = i[1]
        moveTo = i[2]
        var_name = f"t_us_{self.iteration}_{local_iteration}"
        var_reg = '%esi'
        i1 = ["movl", f"{moveFrom}", var_reg]
        i2 = ["movl", var_reg, f"{moveTo}"]        
        return [i1, i2]               
    
    def __unspill_generation__(self):
        new_ir = []
        local_iteration = 0
        # print(f"\n\n\n############################   {self.iteration}\n")
        
        ## If two variables are on stack add temp
        #print("UUUUUUUUUUUUUUUUUUUUUUUU", self.IR)
        print(self.IR)
        for i in self.IR:
            if i[0] != "negl" and len(i) > 1 and i[1] in self.stack_var and i[2] in self.stack_var:
                # print(i)
                if(i[0] == 'addl'):
                    lst = self.__addl_temp_for_stack__(i, local_iteration)
                elif (i[0] == 'movl'):
                    lst = self.__movl_temp_for_stack__(i, local_iteration)
                
                for sublst in lst:
                    new_ir.append(sublst)
                local_iteration += 1
            else:
                new_ir.append(i)
        return new_ir

    
    def assign_register(self):   
        ra = Register_Allocation(self.IR, self.graph.nodes, self.graph.edges, self.allocated_var, self.stack_var, self.unspillable)     
        
        # Check if there is a function call
        ra.check_func_call()        
        ra.create_graph()        
        # Assign variables registers and memory
        ra.color_graph()        
        self.allocated_var, self.stack_var = ra.get_register_allocation()                
        self.iteration += 1        
        self.IR = self.__unspill_generation__()        
        if self.unspillable != None and len(self.unspillable) > 0 and self.iteration < 3:                
            self.IR, self.liveness, self.graph = \
            self.assembler.run_spill_code(self.IR, self.var_order) 
            
            self.assign_register()                                             
        
    def generate_assembly_file(self, assembly, stack_length):
        file_arr = self.file_dir.split("/")
        file_arr[-1] = f"{self.raw_file_name}.s"
        file_arr = "/".join(file_arr)                
        start_template, end_template = base_starter_template(stack_length)
        print("Output", assembly)
        with open(file_arr, 'w') as file:
            file.write(start_template + "\n" + assembly + "\n" + end_template)
            print_("Done saving assembly to file: Success")       

    def call_order(self):
        self.create_assembly_IR()
        self.assign_register() 
        assembly, stack_length = self.assembler.compile_assembly(self.IR, self.allocated_var, self.stack_var)
        self.generate_assembly_file(assembly, stack_length)        
    
if __name__ == "__main__":        
    compilation = Compile_P0()
    #compilation.create_assembly_IR()
    compilation.call_order()