from redbreast.workflow.core.spec import *

def call():
    
    print "Test....."
    wf_spec = WorkflowSpec(name = 'TestWorkFlow')
    wf_spec.dump()

            
if __name__ == '__main__':
    call()
