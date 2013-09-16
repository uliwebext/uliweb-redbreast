from redbreast.core import CoreManager
from redbreast.core.spec import *

class TestCoreSpec(object):
    
    def test_manager(self):
        assert isinstance(CoreManager, WorkflowSpecManager)
    
    def test_manager_add(self):
        wf_spec = WorkflowSpec(name = 'TestWorkFlow')
        CoreManager.add_workflow_spec(wf_spec)
        
        assert wf_spec == CoreManager.get_workflow_spec('TestWorkFlow')
