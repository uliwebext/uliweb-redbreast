#coding=utf8
from redbreast.core.utils import EventDispatcher
from redbreast.core.exception import WorkflowException

class AbstractTaskSpec(object):
    def __init__(self):
        super(AbstractTaskSpec, self).__init__()


class TaskSpec(AbstractTaskSpec, EventDispatcher):
    
    #Events
    EVENT_ENTER    = "event_task_enter"
    EVENT_READY    = "event_task_ready"
    EVENT_EXECUTE  = "event_task_execute"
    EVENT_FINISHED = "event_task_finished"
    
    #

    def __init__(self, workflow_spec, name, **kwargs):
        
        super(TaskSpec, self).__init__()
        
        self.parent = workflow_spec
        self.name = str(name) #unique in workflow
        self.description = kwargs.get('description', '')
        
        self.inputs = []
        self.outputs = []
        
        self.data = kwargs.get('data', {})
        self.parent._notify_addchild(self)
        
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
    
    def connect(self, taskspecs):
        if not isinstance(taskspecs, list):
            taskspecs = [taskspecs]
        for spec in taskspecs:
            self.outputs.append(spec)
            spec._notify_connect(self)
        return taskspecs[-1]
    
    to = connect

    def follow(self, taskspecs):
        if not isinstance(taskspecs, list):
            taskspecs = [taskspecs]
        for spec in taskspecs:
            spec.connect(self)
        return taskspecs[-1]
    
    def __rshift__(self, other):
        return self.to(other)

    def __lshift__(self, other):
        return self.follow(other)

    def __sub__(self, other):
        return self.to(other)
    
    def __neg__(self):
        return self

    def test(self):
        if len(self.inputs) < 1:
            raise WorkflowException(self, 'No input task connected.')
        
    def _notify_connect(self, taskspec):
        self.inputs.append(taskspec)
        
    def __str__(self):
        return "%s (%s)" % (self.name, self.__class__.__name__,)
        

class StartTask(TaskSpec):
    pass

class SimpleTask(TaskSpec):
    pass
    
    
