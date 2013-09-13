import logging

from redbreast.core.exception import WorkflowException
from redbreast.core.spec import *
from redbreast.core.utils import EventDispatcher
from uuid import uuid4
import time

LOG = logging.getLogger(__name__)

class Workflow(EventDispatcher):
    def __init__(self, workflow_spec, **kwargs):
        LOG.debug("__init__ Workflow instance %s" % str(self))
        
        self.spec = workflow_spec
        self.data = {}
        self.parent_workflow = kwargs.get('parent', self)
        
        self.task_tree = Task(self, self.spec.start)
        self.last_task = None
        
    def start(self):
        pass
        
    def get_data(self, name, default=None):
        return self.data.get(name, default)
    
    def run(self):
        while self.run_next():
            pass
        
    def run_all(self):
        self.run()
        
    def run_next(self):
        pass
    
    def run_from_id(self, task_id):
        if task_id is None:
            raise WorkflowException(self.spec, 'task_id is None')
        for task in self.task_tree:
            if task.id == task_id:
                return task.complete()
        msg = 'A task with the given task_id (%s) was not found' % task_id
        raise WorkflowException(self.spec, msg)
        
