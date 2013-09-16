#coding=utf8
from redbreast.core.utils import EventDispatcher, Event
from redbreast.core import WFConst
from manager import WFManager
from task import *

class TaskSpecProxy(object):
    
    def __init__(self, name, task_spec, workflow_spec):
        self.name = name
        self.spec = task_spec
        self.workflow_spec = workflow_spec

    def __getattr__(self, name):
        return getattr(self.spec, name)
        
    def to(self, wrapper):
        #self.outpus.append(wrapper)
        #wrapper._notify_connect(self)
        return wrapper
        
    def follow(self, wrapper):
        wrapper.to(self)
        return wrapper
        
    def __sub__(self, wrapper):
        return self.to(wrapper)
        
    def __neg__(self):
        return self
        self.inputs.append(wrapper)
        
class WorkflowSpec(EventDispatcher):
            
    def __init__(self, name=None):
        super(WorkflowSpec, self).__init__()

        self.name = name or ""
        self.description = ""
        self.task_specs = {}
        self.task_inputs = {}
        self.task_output = {}
        
        start_task = WFManager().get_task_spec(WFConst.TASK_START)
        self.start = TaskSpecProxy(WFConst.TASK_START, start_task, self)
    
    def get_task_spec(self, name):
        return self.task_specs.get(name, None)

    def add_task_spec(self, name, taskspec):
        if name in self.task_specs:
            raise KeyError('Duplicate task spec name: ' + name)

        proxy = TaskSpecProxy(name, taskspec, self)
        self.task_specs[name] = proxy
        self.task_inputs[name] = []
        self.task_outputs[name] = []

        #pubsub
        event = Event(WFConst.EVENT_WF_ADDTASK, 
            self, {
                "task_spec_name": name, 
                "task_spec": task_spec
            })
        self.fire(event)

    def add_flow(self, from_name, to_name):
        if not from_name in self.task_specs:
            raise KeyError('task spec name (%s) does not exist.' % from_name)

        if not to_name in self.task_specs:
            raise KeyError('task spec name (%s) does not exist.' % to_name)

        self.task_outputs.append()


    def get_inputs(self, name):
        pass

    def get_outputs(self, name):
        pass

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
