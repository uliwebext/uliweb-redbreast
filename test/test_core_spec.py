from redbreast.core.spec import CoreWFManager, WFManager
from redbreast.core.spec import *
import pytest

class TestCoreSpec(object):
    
    def setup(self):
        CoreWFManager.reset()
    
    def teardown(self):
        pass
    
    def test_manager(self):
        assert isinstance(CoreWFManager, WFManager)
        assert CoreWFManager == WFManager()
        assert WFManager() == WFManager()
    
    def test_manager_add(self):
        wf_spec = WorkflowSpec(name = 'TestWorkFlow')
        CoreWFManager.add_workflow_spec(wf_spec)
        assert wf_spec == CoreWFManager.get_workflow_spec('TestWorkFlow')
        
    def test_manager_add2(self):
        with pytest.raises(KeyError):
            wf_spec = WorkflowSpec(name = 'TestWorkFlow')
            CoreWFManager.add_workflow_spec(wf_spec)
            CoreWFManager.add_workflow_spec(wf_spec)
            #CoreWFManager.add_workflow_spec(wf_spec)
