"""
Counter that is shared between two different python modules.
Used to test independence.
Not intended to be used as a real example.
"""

counter = 0

def increment_counter():
    global counter
    counter = counter + 1

def reset_counter():
    global counter
    counter = 0
    
def get_counter():
    global counter
    return counter
