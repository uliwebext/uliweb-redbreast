import logging

from redbreast.core.exception import WorkflowException
from redbreast.core.spec import *
from uuid import uuid4
import time

LOG = logging.getLogger(__name__)


class Task(object):
    
    WAITING   =  1
    READY     =  2
    COMPLETED =  4
   
    state_names = {
        WAITING:   'WAITING',
        READY:     'READY',
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
    
    def __init__(object, task_spec, parent=None):
    
        self.workflow = workflow
        self.parent = parent
        self.spec = task_spec
        self.state_history = [state]
        self.state = state
        self.data = {}
        self.id = uuid4()
        
        self.children = []
        if parent is not None:
            self.parent._child_added_notify(self)
        
        
    def __iter__(self):
        return Task.Iterator(self)
    
    def __repr__(self):
        return '<Task object (%s) in state %s at %s>' % (
            self.spec.name,
            self.get_state_name(),
            hex(id(self)))
            
    def _has_state(self, state):
        return (self.state & state) != 0
    
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
    
    def _get_depth(self):
        depth = 0
        task = self.parent
        while task is not None:
            depth += 1
            task = task.parent
        return depth
            
    def _child_added_notify(self, child):
        assert child is not None
        self.children.append(child)
        
    def _drop_children(self):
        drop = []
        for child in self.children:
            if not child._is_finished():
                drop.append(child)
            else:
                child._drop_children()
        for task in drop:
            self.children.remove(task)
    
    def complete(self):
        self._set_state(self.COMPLETED)
        return self.spec._on_complete(self)
    
    def set_data(self, **kwargs):
        self.data.update(kwargs)
    
    def get_data(self, name=None, default=None):
        return self.data.get(name, default)

    def get_spec_data(self, name=None, default=None):
        return self.spec.get_data(name, default)
    
    def get_name(self):
        return str(self.spec.name)
    
    def get_description(self):
        return str(self.task_spec.description)
    
    def get_state(self):
        return self.state
        
    def get_state_name(self):
        state_name = []
        for state, name in self.state_names.iteritems():
            if self._has_state(state):
                state_name.append(name)
        return '|'.join(state_name)
    
    def get_dump(self, indent=0, recursive=True):
        dbg  = (' ' * indent * 2)
        dbg += '%s:'           % self.id
        dbg += ' Task of %s'   % self.get_name()
        if self.spec.description:
            dbg += ' (%s)'   % self.get_description()
        dbg += ' State: %s'    % self.get_state_name()
        dbg += ' Children: %s' % len(self.children)
        if recursive:
            for child in self.children:
                dbg += '\n' + child.get_dump(indent + 1)
        return dbg
    
    def dump(self, indent=0):
        print self.get_dump()
                    
