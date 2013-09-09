#coding=utf8
from redbreast.workflow.core.utils import EventDispatcher
from redbreast.workflow.core.exception import WorkflowException

class TaskEvent(object):
    ENTER    = "task_enter_event"
    READY    = "task_ready_event"
    EXECUTE  = "task_execute_event"
    FINISHED = "task_finished_event"

class TaskSpec(object):
    def __init__(parent, name, **kwargs):
        self.parent = parent
        self.name = str(name)
        self.description = kwargs.get('description', '')
        
        self.inputs = []
        self.outputs = []
        
        self.data = kwargs.get('data', {})
        self.dispatcher = EventDispatcher()
        
        self.parent._addchild_notify(self)
        
    def ancestors(self):
        results = []
    
        def recursive_find_ancestors(task, stack):
            for input in task.inputs:
                if input not in stack:
                    stack.append(input)
                    recursive_find_ancestors(input, stack)
        recursive_find_ancestors(self, results)
    
        return results
    
    def set_data(self, **kwargs):
        for key in kwargs:
            self.data.update(kwargs)

    def get_data(self, name, default=None):
        return self.data.get(name, default)
    
    def connect(self, taskspec):
        self.outputs.append(taskspec)
        taskspec._connect_notify(self)
        
    def follow(self, taskdef):
        taskspec.connect(self)
        
    def test(self):
        if len(self.inputs) < 1:
            raise WorkflowException(self, 'No input task connected.')

class StartTask(TaskSpec):
    pass

class EndTask(TaskSpec):
    pass
    
    
