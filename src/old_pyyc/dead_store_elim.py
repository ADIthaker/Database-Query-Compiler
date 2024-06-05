class Dead_Store:
    
    def __init__(self):
        self.IR = None
        self.live = None
        
        
    def remove_dead_code(self, IR, live):
        self.IR = IR
        self.live = live
        new_IR = []
        
        self.live.insert(0, set())
        
        for inst, live in zip(self.IR, self.live):
            if inst[0] == 'movl':
                if inst[2] not in live:
                    continue
            new_IR.append(inst)
        return new_IR