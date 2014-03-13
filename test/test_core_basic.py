from redbreast.core.spec import *

class TestBasic(object):
    
    def setup(self):
        self.__event_called = False
    
    def teardown(self):
        pass
    
    def test_create_workflowspec(self):
        wf_spec = WorkflowSpec(name = 'TestWorkFlow')
        assert wf_spec != None
        
    def test_addchild_event(self):
        
        wf_spec = WorkflowSpec(name = 'TestWorkFlow')
        
        def addchild(event):
            self.__event_called = True
            
            assert hasattr(event, 'task_spec')
            assert hasattr(event, 'task_spec_name')
            assert event.task_spec.name == "TaskA"
            assert event.task_spec_name == "A"
            
        wf_spec.on("workflow:addchild", addchild)
        wf_spec.add_task_spec('A', SimpleTask("TaskA"))
        
        assert self.__event_called == True
        
    def test_on_addchild_veto(self):
        wf_spec = WorkflowSpec(name = 'TestWorkFlow')
        
        def on_addchild(workflow_spec, task_spec):
            if task_spec.name == "TaskA":
                return False
            return True
        
        wf_spec.on_addchild = on_addchild
        wf_spec.add_task_spec('A', SimpleTask("TaskA"))
        assert wf_spec.get_task_spec('A') == None
        wf_spec.add_task_spec('B', SimpleTask("TaskB"))
        assert wf_spec.get_task_spec('B').name == 'B'
        
        
        
        
        
    
        
        