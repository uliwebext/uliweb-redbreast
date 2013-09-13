from redbreast.core.spec import *

class TestBasic(object):
    
    def setup(self):
        pass
    
    def teardown(self):
        pass
    
    def test_create_workflowspec(self):
        wf_spec = WorkflowSpec(name = 'TestWorkFlow')
        assert wf_spec != None
        
    def test_addchild_event(self):
        self.__event_called = False
        wf_spec = WorkflowSpec(name = 'TestWorkFlow')
        
        def addchild(event):
            self.__event_called = True
            task_spec = event.data.get("task_spec")
            assert task_spec != None
            assert task_spec.name == "TaskA"
            
        wf_spec.on(WorkflowSpec.EVENT_WF_ADDTASK, addchild)
            
        a = SimpleTask(wf_spec, "TaskA")
        
        assert self.__event_called == True
        
    def test_on_addchild_veto(self):
        wf_spec = WorkflowSpec(name = 'TestWorkFlow')
        
        def on_addchild(workflow_spec, task_spec):
            if task_spec.name == "TaskA":
                return False
            return True
        
        wf_spec.on_addchild = on_addchild
        a = SimpleTask(wf_spec, "TaskA")
        assert wf_spec.get_taskspec('TaskA') == None
        b = SimpleTask(wf_spec, "TaskB")
        assert wf_spec.get_taskspec('TaskB') == b
        
        
        
        
        
    
        
        