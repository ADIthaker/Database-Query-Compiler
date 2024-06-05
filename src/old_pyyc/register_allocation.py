

class Register_Allocation:
    def __init__(self, IR, nodes, edges, \
                 allocated_var = None, stack_var = {}, unspillable = None):
        self.graph_nodes = nodes
        self.IR = IR        
        self.edges = edges        
        self.function_call = False
        self.registers = ['eax', 'ecx', 'edx', 'edi', 'ebx', 'esi']               
        
        # Get edge and number of connections
        self.graph = {}
        self.saturation_count = {}
        self.allocated_var = {} \
        if allocated_var is None else allocated_var
        
        self.stack_var = stack_var        
        self.unspillable = [] if unspillable is None else unspillable        
        # print("%%%%%%%%%Spilling unspilling:", self.unspillable)        
        
                
        
    # Check if there is any function call in ast
    def check_func_call(self):
        if any('call' in sublist for sublist in self.IR):
            self.function_call = True        

    def __init_saturation_count__(self):
        for i in self.graph_nodes:
            if i not in self.registers:
                self.saturation_count[i] = 0
    
    def __add_node__(self, k, v):
        # create set if key not there in graph
        if k not in self.graph:
            self.graph[k] = set()
        # Else add to graph set
        self.graph[k].add(v)        
    
    def __add_saturation_count__(self, k):
        self.saturation_count[k] += 1
            
    def __sort_saturation_count__(self):
        self.saturation_count = \
        dict(sorted(self.saturation_count.items(), \
                    key = lambda item: item[1], \
                    reverse = True))
    
    def __sort_graph__(self):
        self.graph = \
        dict(sorted(self.graph.items(), \
                    key = lambda item: len(item[1]), \
                    reverse = True))             
    
    def create_graph(self):
        
        self.__init_saturation_count__()        
        # Add nodes to graph 
        # (Assuming eax, ecx edx are always on idex 1 in edges tuple)               
        for i in self.edges:
            k = i[0]
            v = i[1]            
            
            ##################### Adding edges set to dict
            # Adding k, value 
            # (Assuming eax, ecx edx are always on index 1 in edges tuple (i1, i2))
            self.__add_node__(k, v)                
            
            # Adding reverse direction(v -> k)
            if v not in self.registers: 
                self.__add_node__(v, k)                                
        
        #### Remove later on
        self.__sort_graph__()
        self.__sort_saturation_count__()         
    
    
    def __get_key_value__(self, temp_dict, index):
        if len(temp_dict) > 0:
            # print("TTTTTTDDDDDDD", temp_dict)
            key, value = list(temp_dict.items())[index]        
            return key, value
        return None, None
    
    
    def __select_node_to_color__(self):
        self.__sort_graph__()
        self.__sort_saturation_count__()                
        first_key, first_value = self.__get_key_value__(self.saturation_count, 0)
        last_key, last_value = self.__get_key_value__(self.saturation_count, -1)
                
        # if first_key or last_value == None:
        #     return None
            
        if (len(self.unspillable) > 0):            
            # try:
            item = self.unspillable.pop(0)                     
            return item
        
        ## elif the first and last saturation values are same, 
        ## return first element from graph, (contains highest adjacent edges)
        elif (last_value == first_value):    
            return self.__get_key_value__(self.graph, 0)[0]
                                
        ## Else: 
        else:
            return first_key        
    
    def __remove_node__(self, key):        
        value = self.graph.pop(key, None)            
        value = self.saturation_count.pop(key, None)   
        if key in self.unspillable:
            value = self.unspillable.pop(key, None)        
    
    def __assign_register__(self, key):
        # # is there a function call while this key is assigned a register
        # is_there_a_func_call = True if 'eax' or 'ecx' or 'edx' in key_edge_list else False 
        
        # If stays false through exec, means code spills
        assigned_register = False                            
        
        # 1) All variables are from interfering graph first.        
        key_edge_list = self.graph[key]            

        # Find what register it cannot get assigned to:
        register_it_cannot_be = []
        for node in key_edge_list:
            if node in self.registers:
                register_it_cannot_be.append(node)
            elif node in self.allocated_var:
                register_it_cannot_be.append(self.allocated_var[node])

        # Find the optimum register
        for register in self.registers:            
            if register not in register_it_cannot_be:
                self.allocated_var[key] = register                
                assigned_register = True
                break
                
        # if assigned_register == False and key in self.unspillable:
        #     print("@@@@@@@Spilling unspilling:", key)
            
        ## Handle spill code:                           
        if (assigned_register == False) \
        and (key not in self.allocated_var) \
        and (key not in self.stack_var) \
        and (key not in self.unspillable):

            # Assign stack position based on length of stack_var
            location = len(self.stack_var)            
            self.stack_var[key] = location             
            self.allocated_var[key] = f"-{4 * (location + 1)}(%ebp)"
            assigned_register = True                

        # Variable already in stack
        if assigned_register == False and key in self.stack_var:                            
            assigned_register = True                            

        if assigned_register == False:
            print(f"{key}: Does not qualify for anything")


        # Assign saturation counts to connected edges
        for i in key_edge_list:
            if i in self.saturation_count:
                self.saturation_count[i] += 1                
            
    
    def color_graph(self):        
        # Sort based on saturation       
        # Graph is the inteference graph
        # 1) Clear everything from interferance graph
        # 2) General algorithm with saturation > adjacent edges    
        # print("UUUUUUUUUSSSS", self.unspillable)
        for i in range(len(self.unspillable)):
            self.__assign_register__(self.unspillable[i])
            
        # Remove everything from self.unspillable
        # print("UUUUUUUUUGGG.......", self.graph)    
        for i in range(len(self.graph)):
            # print("UUUUUUUUUGGG.......", self.graph) 
            key = self.__select_node_to_color__()        
            if key == None:
                break
            self.__assign_register__(key)                        
            self.__remove_node__(key)
        
        # print("___From R_Alloc___\n\n")        
        # print("Allocated_var:\n", self.allocated_var, end="\n\n")
        # print("Stack_var:\n", self.stack_var, end="\n\n")                              
        rem_var = []        
        for i in self.graph_nodes:
            if i not in self.allocated_var and i not in self.registers:
                rem_var.append(i)
                
        # print("Remaining Nodes:\n", rem_var, end="\n\n")
        # print("##################################################")      
        
        # exit()            
        for node in self.graph_nodes:                            
            if node not in self.allocated_var and node not in self.registers:
                location = len(self.stack_var)            
                self.stack_var[node] = location                 
                self.allocated_var[node] = f"-{4 * (location + 1)}" 
                
        # print("%%%%%%%%%Spilling after:", self.unspillable)        
        ...
    
    def get_register_allocation(self):
        return self.allocated_var, self.stack_var
        
if __name__ == "__main__":
    IR = [[]]
    nodes = ['t_0', 'x', 'z', 'm', 'n', 'y', 'q', 'eax', 'ecx', 'edx']
    edges = [('t_0', 'eax'), ('t_0', 'edx'), ('t_0', 'ecx'), ('t_0', 'n'), ('m', 'y'), ('n', 'm'), ('m', 'z'), ('z', 'x'), ('x', 'y'), ('y', 'q'), ('t_0', 'y')]
    ra = Register_Allocation(IR, nodes, edges)
    ra.check_func_call()
    ra.create_graph()    
    ra.color_graph()        