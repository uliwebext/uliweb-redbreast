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
    EXECUTING =  4
    EXECUTED  =  8
    COMPLETED = 16
    
    # waiting --> ready()  --> ready
    # ready --> execute() 
    # if async ---> executing
    #    async-callback --> executed
    # if sync --> executed --> route() --> completed
    # executed --> transfer() ---> completed

    state_names = {
        WAITING:   'WAITING',
        READY:     'READY',
        EXECUTING: 'EXECUTING',
        EXECUTED:  'EXECUTED',
        COMPLETED: 'COMPLETED',
    }
    
    class Iterator(object):
        def __init__(self, current, filter=None):
            self.filter = filter
            self.path = [current]
    
        def __iter__(self):
            return self
    
        def _next(self):
            if len(self.path) == 0:
                raise StopIteration()
            
            current = self.path[-1]
            if current.children:
                self.path.append(current.children[0])
                if self.filter is not None and current.state & self.filter == 0:
                    return None
                return current
            
            while True:
                old_child = self.path.pop(-1)
                if len(self.path) == 0:
                    break;
                
                parent = self.path[-1]
                pos = parent.children.index(old_child)
                if len(parent.children) > pos + 1:
                    self.path.append(parent.children[pos + 1])
                    break
                return current
    
        def next(self):
            while True:
                next = self._next()
                if next is not None:
                    return next
    
    
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
            
    def __iter__(self):
        return Task.Iterator(self)
            
    def _getstate(self):
        return self._state
    
    def _setstate(self, value):
        if self._state == value:
            return
        old = self.get_state_name()
        self._state = value
        self.state_history.append(value)
        self.last_state_change = time.time()
        
        LOG.debug("Moving '%s' from %s to %s" % 
            (self.get_name(), old, self.get_state_name()))
            
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
    
    def get_name(self):
        return self.spec.name

    def add_child(self, child):
        self.children.append(child)
        
    def ready(self):
        return self.spec.ready(self, self.workflow)
    
    def execute(self):
        return self.spec.execute(self, self.workflow)
    
    def route(self):
        return self.spec.execute(self, self.workflow)
        
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
        # Walk through all waiting tasks.
        for task in Task.Iterator(self.task_tree, Task.WAITING):
            #task.task_spec._update_state(task)
            if not task._has_state(Task.WAITING):
                self.last_task = task
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
        
