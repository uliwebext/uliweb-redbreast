#coding=utf8
from redbreast.core.utils import EventDispatcher
from redbreast.core.exception import WFException

class TaskSpec(object):
    task_type = 'Task'
    def __init__(self, name, **kwargs):
        super(TaskSpec, self).__init__()
        self.name = str(name) #unique in workflow
        self.desc = kwargs.get('desc', '')
        
    def __str__(self):
        return "%s (%s)" % (self.name, self.__class__.__name__)
    
    def get_type(self):
        return self.task_type or 'SimpleTask'
        

class StartTask(TaskSpec):
    task_type = 'StartTask'
    def __init__(self):
        from redbreast.core import WFConst
        super(StartTask, self).__init__(WFConst.TASK_START)

class SimpleTask(TaskSpec):
    task_type = 'SimpleTask'
    
    
