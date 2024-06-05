import ast
from ast import *
from collections import defaultdict

class Assembler:
    def __init__(self, flat_code):
        self.flat_code = flat_code
        self.var_dict = {}
        self.IR = []
        self.cmd_ls = defaultdict(list)
    
    def IR_generation(self):
        for block in self.flat_code:
            if block['type'] == "select":
                if 'where' in block and 'orderBy' not in block:
                    self.IR.append(["select", block['select'], block['table_name'], block['where'], ""])
                elif 'orderBy' in block and 'where' not in block:
                    self.IR.append(["select", block['select'], block['table_name'], "", block['orderBy']])
                elif 'orderBy' not in block and 'where' not in block:
                    self.IR.append(["select", block['select'], block['table_name'], "", ""])
                else:
                    self.IR.append(["select", block['select'], block['table_name'], block['where'], block['orderBy']])
                if 'view' in block:
                    self.IR.append(['view', block['view']]) # add command to make view of the select that ends before it.

            elif block['type'] == "update":
                self.IR.append(["update", block['set'], block['table_name']])

            elif block['type'] == "delete":
                if 'where' in block:
                    self.IR.append(["delete", block['where'], block['table_name']])
                else:
                    self.IR.append(["delete", "", block['table_name']])

            elif block['type'] == "index":
                pass

            elif block['type'] == "flat_block":
                for inst in block["flat_expr"]:
                    flat_ast = ast.parse(inst)
                    if isinstance(flat_ast, Module):
                        for st in flat_ast.body:
                            if isinstance(st, Assign):
                                tar = st.targets[0].id
                                val = st.value
                                if isinstance(val, Compare):
                                    if isinstance(val.ops[0], Eq):
                                        self.IR.append(["equals", val.left.id, val.comparators[0].id, tar])
                                    elif (val.ops[0], NotEq):
                                        self.IR.append(["nequals", val.left.id, val.comparators[0].id, tar])
                                    elif isinstance(val.ops[0], Lt):
                                        self.IR.append(["lt", val.left.id, val.comparators[0].id, tar])
                                    elif isinstance(val.ops[0], LtE):
                                        self.IR.append(["lte", val.left.id, val.comparators[0].id, tar])
                                    elif isinstance(val.ops[0], Gt):
                                        self.IR.append(["gt", val.left.id, val.comparators[0].id, tar])
                                    elif isinstance(val.ops[0], GtE):
                                        self.IR.append(["gte", val.left.id, val.comparators[0].id, tar])
                                elif isinstance(val, BoolOp):
                                    if isinstance(val.op, And):
                                        self.IR.append(["and", val.values[0].id, val.values[1].id, tar])
                                    elif isinstance(val.op, Or):
                                        self.IR.append(["or", val.values[0].id, val.values[1].id, tar])
                                elif isinstance(val, UnaryOp):
                                    if isinstance(val.op, Not):
                                        self.IR.append(["not", val.operand.id, tar])
                    print(ast.dump(flat_ast, indent=2))
            elif block['type'] == "import_table":
                pass


    def optimize_batch_processing(self):
        for idx, inst in enumerate(self.IR):
            if inst[0] == 'select':
                self.cmd_ls['select'].append((idx, inst[1], inst[2], inst[3], inst[4])) #(line, col_ls, table, cond, orderBy)
        
        for i in range(len(self.cmd_ls)):
            for j in range(len(self.cmd_ls)):
                if i != j:
                    
                # loop over all selects and find which one you can replace with.
        # if 2 consecutive selects on same table without an update to that table, merge the cols of both selects. dont merge if a view is in between any of the selects.
        # if 2 consecutive selects, and one has a an orderBy. order after making 2 selects.
        # mechanism to find out if one select is a subset of the other.

        # if delete called on table without condition, remove all future select and updates that have this table.

        # if 2 indexes created on same table without update remove the latest one.
        # if 2 views created on same table without update remove the latest one.

    def _lvn(self, bb):
        # always gets the basic blocks
        print("DOING BLOCK", bb)
        current_value = -1
        value_numbers = dict()
        is_constant = defaultdict(lambda: False)
        constant_values = dict() 
        
        def get_curr_val():
            nonlocal current_value
            current_value += 1
            return current_value
        
        get_old_val = lambda x,y : value_numbers[f"{x}+{y}"] if f"{x}+{y}" in value_numbers else get_curr_val()
        #this will only work for compile time vars need to allocate value to runtime vars also
        
        for idx in range(bb[0], bb[1]+1):
            print("\n\n")
            inst = self.IR[idx]
            print(idx, inst)
            
            if inst[0] == "hset":
                if isinstance(inst[1], int):
                    value_numbers[inst[1]] = get_curr_val() # if the first operand is an int, assign it a value else we know that it will be live
                    is_constant[inst[2]] = True
                    constant_values[inst[2]] = inst[1]
                elif is_constant[inst[1]]:
                    self.IR[idx] = ["hset", constant_values[inst[1]], inst[2]]
                    is_constant[inst[2]] = True
                    constant_values[inst[2]] = constant_values[inst[1]]
                    
                elif not is_constant[inst[1]]:
                    try:
                        del constant_values[inst[2]]
                        del is_constant[inst[2]]
                    except KeyError:
                        pass
                #value numbering
                if inst[1] in value_numbers:
                    value_numbers[inst[2]] = value_numbers[inst[1]]
                else:
                    value_numbers[inst[1]] = get_curr_val()
                    value_numbers[inst[2]] = value_numbers[inst[1]]
                                
            print("VALUE_NUMBERS", value_numbers)
            print("Constants", is_constant)
            print("Constant Values", constant_values)
            print("SUBBED INST", self.IR[idx])
        
flat_code = [{'type': 'flat_block', 'flat_expr': ['condition1 = last_name < Smith', 'condition2 = first_name != Alfred', 'condition3 = condition1 and condition2', 'a = not b']},
{'select': ['*'], 'table_name': 'CUSTOMERS', 'orderBy': ('col1', 'DESC'), 'type': 'select'},
{'select': ['col1', 'col2'], 'table_name': 'CUSTOMERS', 'type': 'select'},
{'select': ['col1', 'col2'], 'table_name': 'CUSTOMERS', 'where': 'condition3', 'type': 'select'},
{'set': 'condition3', 'table_name': 'CUSTOMERS', 'type': 'update'},
{'table_name': 'CUSTOMER', 'type': 'delete'},
{'type': 'flat_block', 'flat_expr': ['del_cond = first_name != Alfred']},
{'table_name': 'CUSTOMER', 'where': 'del_cond', 'type': 'delete'},
{'url': 'http://example.com', 'short_table_name': 'CUSTOMERS', 'header': 'False', 'type': 'import_table'},
{'table_name': 'index_name', 'select': ['*'], 'url': './data/zillow.csv', 'short_table_name': 'CUSTOMERS', 'header': 'False', 'type':'import_table'}]

assm = Assembler(flat_code)
assm.IR_generation()
for inst in assm.IR:
    print(inst)