#coding=utf8
from redbreast.core.utils import EventDispatcher
from redbreast.core.exception import WFException

class TaskSpec(object):

    def __init__(self, name, **kwargs):
        super(TaskSpec, self).__init__()
        self.name = str(name) #unique in workflow
        self.description = kwargs.get('description', '')
        
    def __str__(self):
        return "%s (%s)" % (self.name, self.__class__.__name__,)
        

class StartTask(TaskSpec):
    def __init__(self):
        from redbreast.core import WFConst
        super(StartTask, self).__init__(WFConst.TASK_START)

class SimpleTask(TaskSpec):
    pass
    
    
