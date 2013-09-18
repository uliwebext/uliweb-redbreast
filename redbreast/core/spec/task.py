#coding=utf8
from redbreast.core.utils import EventDispatcher
from redbreast.core.exception import WFException
from redbreast.core import WFConst

class TaskSpec(object):
    task_type = 'Task'
    __supported_config_fields__ = []
    def __init__(self, name, **kwargs):
        super(TaskSpec, self).__init__()
        self.name = str(name) #unique in workflow
        self.desc = kwargs.get('desc', '')
        
    def __str__(self):
        return "%s (%s)" % (self.name, self.__class__.__name__)
    
    def get_type(self):
        return self.task_type or 'SimpleTask'
    
    def update_kwarg(self, data):
        for key in data:
            if key in self.__supported_config_fields__:
                setattr(self, key, data[key])
                
    def ready(self, task, workflow):
        from redbreast.core import Task
        task.state = Task.READY
        #pubsub
        workflow.spec.fire(WFConst.EVENT_TASK_READY,
            task=task, workflow=workflow)
        return True
        
    def execute(self, task, workflow):
        from redbreast.core import Task
        task.state = Task.EXECUTED
        #pubsub
        workflow.spec.fire(WFConst.EVENT_TASK_EXECUTED,
            task=task, workflow=workflow)
        return True
        
    def transfer(self, task, workflow):
        from redbreast.core import Task
        
        for task_spec in task.spec.outputs:
            new_task = Task(workflow, task_spec, parent=task)
            task.add_child(new_task)
        
        task.state = Task.COMPLETED
        #pubsub
        workflow.spec.fire(WFConst.EVENT_TASK_COMPLETED,
            task=task, workflow=workflow)
        return True

class StartTask(TaskSpec):
    task_type = 'StartTask'
    def __init__(self):
        from redbreast.core import WFConst
        super(StartTask, self).__init__(WFConst.TASK_START)

class SimpleTask(TaskSpec):
    task_type = 'SimpleTask'
    
    
