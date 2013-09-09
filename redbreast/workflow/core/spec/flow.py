#coding=utf8
from redbreast.workflow.core.utils import EventDispatcher
from task import *

class WorkflowEvent(object):
    BEFORE_ADDTASK = "before_add_task"
    ADDTASK = "add_task"

class WorkflowSpec(object):
    
    def __init__(self, name=None):
        
        self.name = name or ''
        self.description = ''
        self.task_specs = dict()
        self.start = StartTask()
        
        self.dispatcher = EventDispatcher()
        
    def validate(self):
        return True
    
    def serialize(self):
        pass
    
    def deserialize(self):
        pass
    
    def dump(self):
        print "-------------------------------------------"
        print "Workflow: %s" % self.name
        for task in self.task_specs :
            print task
        print "-------------------------------------------"
        
        
    def _addchild_notify(self, task_spec):
        if task_spec.name in self.task_specs:
            raise KeyError('Duplicate task spec name: ' + task_spec.name)
        self.task_specs[task_spec.name] = task_spec
        task_spec.id = len(self.task_specs)
