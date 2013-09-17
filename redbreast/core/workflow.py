import logging

from redbreast.core.exception import WFException
from redbreast.core.spec import *
from redbreast.core.utils import EventDispatcher
from uuid import uuid4
import time

LOG = logging.getLogger(__name__)

class Task(object):

    WAITING   =  1
    READY     =  2
    EXECUTING =  3
    EXECUTED  =  4
    COMPLETED =  5
    
    # waiting --> ready()  --> ready
    # ready --> execute() 
    # if async ---> executing
    #    async-callback --> executed
    # if sync --> executed --> route() --> completed
    # executed --> route() ---> completed

    state_names = {
        WAITING:   'WAITING',
        READY:     'READY',
        EXECUTING: 'EXECUTING',
        EXECUTED:  'EXECUTED',
        COMPLETED: 'COMPLETED',
    }
    
    def __init__(self, workflow, task_spec, parent=None, state=WAITING):
        self.workflow = workflow
        self.spec = task_spec
        self.parent = parent
        self.state_history = [state]
        
        self._state = state
        self.data = {}
        
        self.id = uuid4()
        self.children = []
        if parent is not None:
            self.parent.add_child(self)
            
    def _getstate(self):
        return self._state
    
    def _setstate(self, value):
        if self._state == value:
            return
        old = self.get_state_name()
        self._state = value
        self.state_history.append(value)
        self.last_state_change = time.time()
        
        LOG.debug("Moving '%s' (spec=%s) from %s to %s" % (self.get_name(),
                    self.spec.name, old, self.get_state_name()))
            
    def _delstate(self):
        del self._state
    
    state = property(_getstate, _setstate, _delstate, "State property.")
        
    def get_level(self):
        level = 0
        task = self.parent
        while task is not None:
            level += 1
            task = task.parent
        return level
    
    def get_state_name(self):
        return self.state_names.get(self.state, None)

    def add_child(self, child):
        self.children.append(child)
        
    def ready(self):
        return self.spec.ready(task)
    
    def execute(self):
        return self.spec.execute(task)
    
    def route(self):
        return self.spec.execute(task)
        
    def __repr__(self):
        return '<Task (%s) in state %s at %s>' % (
            self.spec.name,
            self.get_state_name(),
            hex(id(self)))

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
        
        self.spec = workflow_spec
        self.data = {}
        self.parent_workflow = kwargs.get('parent', self)
        
        self.task_tree = Task(self, self.spec.start)
        self.last_task = None
        
        self.state = self.CREATED
        
    def get_data(self, name, default=None):
        return self.data.get(name, default)
    
    def get_state_name(self):
        return self.state_names.get(self.state, None)

    def start(self):
        self.state = self.RUNNING
        ret = self.task_tree.ready()
        if ret:
            self.task_tree.execute()
        
    def run(self):
        while self.run_next():
            pass
        
    def run_all(self):
        self.run()
        
    def run_next(self):
        pass
    
    def run_from_id(self, task_id):
        if task_id is None:
            raise WFException(self.spec, 'task_id is None')
        for task in self.task_tree:
            if task.id == task_id:
                return task.complete()
        msg = 'A task with the given task_id (%s) was not found' % task_id
        raise WFException(self.spec, msg)
        
