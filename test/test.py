from redbreast.workflow.core.spec import *

def addchild(event):
    print "...add child event....."
    print  event.data.get("task_spec")
    print "  target:" , event.target
    print "  event_type:" , event.type
    print "...."

def call():
    
    
    print "Test....."
    wf_spec = WorkflowSpec(name = 'TestWorkFlow')
    
    
    wf_spec.on(WorkflowSpec.EVENT_WF_ADDTASK, addchild)
    
    #  A--B--C   --G--H
    #  A--D--E--F--G--H
    
    #Tasks
    a = SimpleTask(wf_spec, "TaskA")
    b = SimpleTask(wf_spec, "TaskB")
    c = SimpleTask(wf_spec, "TaskC")
    d = SimpleTask(wf_spec, "TaskD")
    e = SimpleTask(wf_spec, "TaskE")
    f = SimpleTask(wf_spec, "TaskF")
    g = SimpleTask(wf_spec, "TaskG")
    h = SimpleTask(wf_spec, "TaskH")
    
    #Links
    wf_spec.start >> a
    
    a -- b -- c -- g -- h
    a -- d -- e -- f -- g
    
    wf_spec.dump()

            
if __name__ == '__main__':
    call()
