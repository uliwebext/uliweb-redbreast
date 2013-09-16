#coding=utf8
from redbreast.core.utils import EventDispatcher, Event, Delegate
from redbreast.core import WFConst
from manager import WFManager
from task import *

class WorkflowSpec(EventDispatcher):
    class Proxy(Delegate):
        delegated_methods = ('__str__', 'get_type')  
        
        def __init__(self, name, task_spec, workflow_spec):
            super(WorkflowSpec.Proxy, self).__init__(task_spec)
            self.name = name
            self.workflow_spec = workflow_spec
            
        @property
        def inputs(self):
            return self.workflow_spec.get_inputs(self.name)
        
        @property
        def outputs(self):
            return self.workflow_spec.get_outputs(self.name)
        
        @property
        def type(self):
            return self.get_type()
           
        def to(self, proxy):
            self.workflow_spec.add_flow(self.name, proxy.name)
            return proxy
            
        def follow(self, proxy):
            wrapper.to(self)
            return wrapper
            
        def __sub__(self, proxy):
            return self.to(proxy)
            
        def __neg__(self):
            return self
            
    def __init__(self, name=None):
        super(WorkflowSpec, self).__init__()

        self.name = name or ""
        self.description = ""
        self.task_specs = {}
        self.task_inputs = {}
        self.task_outputs = {}
        
        start_task = WFManager().get_task_spec(WFConst.TASK_START)
        self.start = self.add_task_spec(WFConst.TASK_START, start_task)
    
    def get_task_spec(self, name):
        return self.task_specs.get(name, None)

    def add_task_spec(self, name, task_spec):
        print name
        if name in self.task_specs:
            raise KeyError('Duplicate task spec name: ' + name)

        proxy = WorkflowSpec.Proxy(name, task_spec, self)
        self.task_specs[name] = proxy
        self.task_inputs[name] = []
        self.task_outputs[name] = []

        #pubsub
        self.fire(WFConst.EVENT_WF_ADDTASK, task_spec_name=name, task_spec=task_spec)
        return proxy

    def add_flow(self, from_name, to_name):
        if not from_name in self.task_specs:
            raise KeyError('task spec name (%s) does not exist.' % from_name)

        if not to_name in self.task_specs:
            raise KeyError('task spec name (%s) does not exist.' % to_name)

        self.task_outputs[from_name].append(self.get_task_spec(to_name))
        self.task_inputs[to_name].append(self.get_task_spec(from_name))

    def get_inputs(self, name):
        return self.task_inputs.get(name, [])

    def get_outputs(self, name):
        return self.task_outputs.get(name, [])

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
                return  '[shown earlier] %s (%s)' % (task_spec.name, task_spec.type) + '\n'
    
            done.add(task_spec)
            dump = '%s (%s)' % (task_spec.name, task_spec.type) + '\n'
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
