class Calculator(object):
    
    def __init__(self):
        self.args = []
    
    def push(self, value):
        self.args.append(value)
    
    def add(self):
        return sum(self.args)
    
    def divide(self):
        return float(self.args[0]) / float(self.args[1])

