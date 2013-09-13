#coding=utf8
from redbreast.core.utils import EventDispatcher, Event
from redbreast.core import WFConst
from manager import WFCoreManager
from task import *

class Node(object):
    
    def __init__(self, id, task_spec, workflow_spec):
        self.id = id
        self.inputs = []
        self.outputs = []
        self.spec = task_spec
        self.workflow_spec = workflow_spec
        
    def to(self, wrapper):
        self.outpus.append(wrapper)
        wrapper._notify_connect(self)
        return wrapper
        
    def follow(self, wrapper):
        wrapper.to(self)
        return wrapper
        
    def __sub__(self, wrapper):
        return self.to(wrapper)
        
    def __neg__(self):
        return self
    
    def _notify_connect(self, wrapper):
        self.inputs.append(wrapper)
        

class AbstractWorkflowSpec(object):
    def __init__(self):
        super(AbstractWorkflowSpec, self).__init__()

class WorkflowSpec(AbstractWorkflowSpec, EventDispatcher):
            
    def __init__(self, name=None):
        super(WorkflowSpec, self).__init__()

        self.name = name or ""
        self.description = ""
        self.task_specs = dict()
        
        #veto methods
        self.on_addchild = None
        start_task = WFCoreManager.get_task_spec(WFConst.TASK_START)
        self.start = Node(WFConst.TASK_START, start_task, self)
        
    def get_taskspec(self, name):
        return self.task_specs.get(name, None)
        
    def validate(self):
        return True
    
    def serialize(self):
        pass
    
    def deserialize(self):
        pass
    
    def get_dump(self, verbose=False):
        done = set()
    
        def recursive_dump(task_spec, indent):
            if task_spec in done:
                return  '[shown earlier] %s (%s)' % (task_spec.name, task_spec.__class__.__name__) + '\n'
    
            done.add(task_spec)
            dump = '%s (%s)' % (task_spec.name, task_spec.__class__.__name__) + '\n'
            if verbose:
                if task_spec.inputs:
                    dump += indent + '-  IN: ' + ','.join(['%s' % t.name for t in task_spec.inputs]) + '\n'
                if task_spec.outputs:
                    dump += indent + '- OUT: ' + ','.join(['%s' % t.name for t in task_spec.outputs]) + '\n'
            sub_specs = ([task_spec.spec.start] if hasattr(task_spec, 'spec') else []) + task_spec.outputs
            for i, t in enumerate(sub_specs):
                dump += indent + '   --> ' + recursive_dump(t,indent+('   |   ' if i+1 < len(sub_specs) else '       '))
            return dump
    
    
        dump = recursive_dump(self.start, '')
    
        return dump
    
    def dump(self):
        print "-------------------------------------------"
        print "Workflow: %s" % self.name
        print self.get_dump()
        print "-------------------------------------------"
       
    def _notify_addchild(self, task_spec):
        if task_spec.name in self.task_specs:
            raise KeyError('Duplicate task spec name: ' + task_spec.name)
        
        #veto
        if not self.on_addchild or self.on_addchild(self, task_spec):
            self.task_specs[task_spec.name] = task_spec
            task_spec.id = len(self.task_specs)
            
            #pubsub
            event = Event(WorkflowSpec.EVENT_WF_ADDTASK, self, {"task_spec": task_spec})
            self.fire(event)
            
            
