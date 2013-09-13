from redbreast.core.spec import *
from redbreast.core.spec import WFCoreManager

def call():
    
    print "Test....."
    wf_spec = WorkflowSpec(name = 'TestWorkFlow')
    
    
    #  A--B--C   --G--H
    #  A--D--E--F--G--H
    
    #Tasks
    a = SimpleTask("TaskA")
    b = SimpleTask("TaskB")
    c = SimpleTask("TaskC")
    d = SimpleTask("TaskD")
    e = SimpleTask("TaskE")
    f = SimpleTask("TaskF")
    g = SimpleTask("TaskG")
    h = SimpleTask("TaskH")
    
    
    
    #Links
    wf_spec.start -- a
    
    a -- b -- c -- g -- h
    a -- d -- e -- f -- g
    
    wf_spec.dump()

            
if __name__ == '__main__':
    call()
