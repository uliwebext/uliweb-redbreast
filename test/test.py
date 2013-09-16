from redbreast.core.spec import *
from redbreast.core.spec import WFManager

def call():
    
    print "Test....."
    wf_spec = WorkflowSpec(name = 'TestWorkFlow')
    
    
    #  A--B--C   --G--H
    #  A--D--E--F--G--H
    
    #Create task spec
    A = SimpleTask("TaskA")
    B = SimpleTask("TaskB")
    C = SimpleTask("TaskC")
    D = SimpleTask("TaskD")
    E = SimpleTask("TaskE")
    F = SimpleTask("TaskF")
    G = SimpleTask("TaskG")
    H = SimpleTask("TaskH")
    
    
    #Tasks
    a = wf_spec.add_task_spec("TaskA", A)
    b = wf_spec.add_task_spec("TaskB", A)
    c = wf_spec.add_task_spec("TaskC", A)
    d = wf_spec.add_task_spec("TaskD", A)
    e = wf_spec.add_task_spec("TaskE", A)
    f = wf_spec.add_task_spec("TaskF", A)
    g = wf_spec.add_task_spec("TaskG", A)
    h = wf_spec.add_task_spec("TaskH", A)
    
    #Links
    wf_spec.start -- a
    
    a -- b -- c -- g -- h
    a -- d -- e -- f -- g
    
    wf_spec.dump()

            
if __name__ == '__main__':
    call()
