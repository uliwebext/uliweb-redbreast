import logging

from redbreast.core import WFException
from redbreast.core.spec import *
from redbreast.core.utils import EventDispatcher
from uuid import uuid4
from task import Task

import time

LOG = logging.getLogger(__name__)

class Workflow(EventDispatcher):
    
    CREATED   =  1
    RUNNING   =  2
    FINISHED  =  4
    
    state_names = {
        CREATED:   'CREATED',
        RUNNING:   'RUNNING',
        FINISHED:  'FINISHED',
    }
    
    def __init__(self, workflow_spec, **kwargs):
        
        LOG.debug("__init__ Workflow instance %s" % str(self))
        
        super(Workflow, self).__init__()
        
        self.spec = workflow_spec
        self.Task = kwargs.get('task_klass', Task)
        self.data = {}
        self.parent_workflow = kwargs.get('parent', self)
        
        
        self.task_tree = None
        self.last_task = None
        
        self.state = self.CREATED
        
        #pubsub
        self.spec.fire("workflow:created", workflow=self)
        self.fire("workflow:state_changed", workflow=self)
        
    def get_alldata(self):
        return self.data
    
    def get_data(self, name, default=None):
        return self.data.get(name, default)
    
    def get_state_name(self):
        return self.state_names.get(self.state, None)
    
    def is_multiple_start(self):
        return self.spec.is_multiple_start

    def start(self, start=None):
        #multipe start tasks
        if self.spec.is_multiple_start:
            if not start :
                raise WFException('You must choose which task to start for mulitple-starts workflow')
            
            start_task = self.spec.get_task_spec(start)
            if not start_task:
                names = ','.join(self.spec.get_start_names())
                raise WFException('The node you picked up does not exists in [%s]' % (names))
            self.task_tree = self.Task(self, start_task)
        else:
            self.task_tree = self.Task(self, self.spec.start)
            
        self.state = self.RUNNING
        #pubsub
        self.spec.fire("workflow:running", workflow=self)
        self.fire("workflow:state_changed", workflow=self)
        self.task_tree.is_ready()
        
    def run(self):
        while self.run_next():
            pass
        
    def run_all(self):
        self.run()
        
    def run_next(self):
        # Walk through all waiting tasks.
        for task in Task.Iterator(self.task_tree, Task.READY):
            #task.task_spec._update_state(task)
            print "xxxxxxxxxxxxxxxxxxxxxx", task
            if task._getstate() == Task.READY:
                self.last_task = task
                task.do_execute(transfer=True)
                return True
        return False
    
    def run_from_id(self, task_id):
        if task_id is None:
            raise WFException(self.spec, 'task_id is None')
        for task in self.task_tree:
            if task.id == task_id:
                return task.complete()
        msg = 'A task with the given task_id (%s) was not found' % task_id
        raise WFException(self.spec, msg)
    
    def finish(self):
        #pubsub
        self.spec.fire("workflow:finished", workflow=self)
        self.fire("workflow:state_changed", workflow=self)
        
        
