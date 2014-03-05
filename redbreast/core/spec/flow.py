#coding=utf8
from redbreast.core.utils import EventDispatcher, Event, Delegate
from redbreast.core import WFEventException
from result import inject_const_scope

from task import *

__WF_EVENTS__ = [
    #-- TASK EVENTS
    "task:enter", "task:ready", "task:executed",
    "task:executing", "task:completed",
    #-- WORKFLOW EVENTS
    "workflow:created", "workflow:running", "workflow:paused",
    "workflow:finished", "workflow:addchild"]
__WF_EVENTS_SHORT__ = dict([(e.split(":")[1], e) for e in __WF_EVENTS__])

#TaskProxy FlowType
__FLOW_START__   =  "flowStart"    #StartTask, only have output tasks
__FLOW_END__     =  "flowEnd"      #EndTask, only have input tasks
__FLOW_NORMAL__  =  "flowNormal"   #NormalTask, both have input and output tasks
__FLOW_SINGLE__  =  "flowSingle"   #SingleTask, no inut and no output

class WorkflowSpec(object):

    class Proxy(Delegate):
        delegated_methods = ('__str__', 'get_type', 'is_default',
                'is_ready', 'do_execute', 'do_transfer', 'join_ready')

        def __init__(self, name, task_spec, workflow_spec):
            super(WorkflowSpec.Proxy, self).__init__(task_spec)
            self.name = name
            self.workflow_spec = workflow_spec
            self.flow_type = __FLOW_SINGLE__

        def is_start(self):
            return self.flow_type == __FLOW_START__

        def is_end(self):
            return self.flow_type == __FLOW_END__

        def is_single(self):
            return self.flow_type == __FLOW_SINGLE__

        @property
        def inputs(self):
            return self.workflow_spec.get_inputs(self.name)

        @property
        def outputs(self):
            return self.workflow_spec.get_outputs(self.name)

        @property
        def type(self):
            return self.get_type()

        def get_spec_name(self):
            return self.delegate.name

        def get_desc(self):
            return self.delegate.desc

        def get_ancestors(self):

            map = {}
            def __get_them__(proxy, map):
                for p in proxy.inputs:
                    if not p.name in map:
                        map[p.name] = p
                    __get_them__(p, map)

            __get_them__(self, map)
            return map

        def get_code(self, fnc_name):
            return self.workflow_spec.get_code(self.name, fnc_name)

        def refresh_flow_type(self):
            input_count = len(self.inputs)
            output_count = len(self.outputs)
            if input_count == 0 and output_count == 0:
                self.flow_type = __FLOW_SINGLE__
            else:
                if input_count == 0:
                    self.flow_type = __FLOW_START__
                elif output_count == 0:
                    self.flow_type = __FLOW_END__
                else:
                    self.flow_type = __FLOW_NORMAL__
            return self.flow_type

        def validate(self):
            return self.delegate.validate(self, self.inputs, self.outputs)

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

    __supported_config_fields__ = []

    def __init__(self, name=None, **kwargs):
        from manager import WFManager

        super(WorkflowSpec, self).__init__()

        self.name = name or ""
        self.desc = kwargs.get('desc', '')
        self.task_specs = {}
        self.task_inputs = {}
        self.task_outputs = {}

        self._code_strs = {} #cache config code str
        self._codes = {}     #cache executed function def

        #veto methods
        self.on_addchild = None

        self.is_multiple_start = False
        self.start = None
        self.start_tasks = None

        #MYTODO
        self.is_multiple_end = False
        self.end = None
        self.end_tasks = None

        self.dispatcher = EventDispatcher()

    def dispatch_event(self, event_type, **attrs):
        return self.dispatcher.fire(event_type, **attrs)

    fire = dispatch_event

    def on(self, event_type, listener):

        if event_type == "*":
            for etype in __WF_EVENTS__:
                self.dispatcher.on(etype, listener)

            return

        if event_type in __WF_EVENTS__:
            return self.dispatcher.on(event_type, listener)
        else:
            if event_type in __WF_EVENTS_SHORT__:
                event_type = __WF_EVENTS_SHORT__[event_type]
                return self.dispatcher.on(event_type, listener)

            raise WFEventException("ERROR, '%s' is an unsupport event." % event_type)

    def get_task_spec(self, name):
        return self.task_specs.get(name, None)

    def add_task_spec(self, name, task_spec):
        if name in self.task_specs:
            raise KeyError('Duplicate task spec name: ' + name)

        if not self.on_addchild or self.on_addchild(self, task_spec):
            proxy = WorkflowSpec.Proxy(name, task_spec, self)
            self.task_specs[name] = proxy
            self.task_inputs[name] = []
            self.task_outputs[name] = []

            #pubsub
            self.fire("workflow:addchild", task_spec_name=name, task_spec=task_spec)
            return proxy
        return None

    def add_flow(self, from_name, to_name):
        if not from_name in self.task_specs:
            raise KeyError('task spec name (%s) does not exist.' % from_name)

        if not to_name in self.task_specs:
            raise KeyError('task spec name (%s) does not exist.' % to_name)

        to_task = self.get_task_spec(to_name)
        from_task = self.get_task_spec(from_name)

        self.task_outputs[from_name].append(to_task)
        self.task_inputs[to_name].append(from_task)

        to_task.refresh_flow_type()
        from_task.refresh_flow_type()

    def __set_start_task(self, name):
        if name in self.task_specs:
            if self.is_multiple_start:
                self.start_tasks[name] = self.get_task_spec(name)
            else:
                if not self.start:
                    self.start = self.get_task_spec(name)
                else:
                    self.start_tasks = {}
                    self.start_tasks[self.start.name] = self.start
                    self.start_tasks[name] = self.get_task_spec(name)
                    self.is_multiple_start = True

    def refresh_flow_type(self):
        self.is_multiple_start = False
        self.start = None
        self.start_tasks = None

        for spec in self.task_specs:
            task = self.task_specs[spec]
            if task.is_start():
                self.__set_start_task(spec)

    def update_fields(self, data):
        for key in data:
            if key in self.__supported_config_fields__:
                setattr(self, key, data[key])

    def update_codes(self, data):

        fixed_param = "(task, workflow):"

        for key in data:
            update_str = data[key].replace("():", fixed_param, 1)
            self._code_strs[key] = update_str
            scope = {}
            scope = inject_const_scope(scope)
            exec(update_str, scope)
            self._codes[key] = scope[key]

    def get_code(self, task_name, fnc_name):
        key = "%s_%s_%s" % (self.name, task_name, fnc_name)
        return self._codes.get(key, None)

    def get_inputs(self, name):
        return self.task_inputs.get(name, [])

    def get_outputs(self, name):
        return self.task_outputs.get(name, [])

    def validate(self):
        for spec in self.task_specs:
            self.task_specs[spec].validate()

    def serialize(self):
        pass

    def deserialize(self):
        pass

    def get_start_names(self):
        names = []
        if not self.is_multiple_start:
            names.append(self.start.name)
        else:
            for task in self.start_tasks:
                names.append(task)
        return names

    def get_dump(self, verbose=False):
        done = set()

        def recursive_dump(task_spec, indent):
            if task_spec in done:
                return  '[shown earlier] %s (%s)' % (task_spec.name, task_spec.type) + '\n'

            done.add(task_spec)

            if task_spec.is_end():
                dump = '%s (%s-End)' % (task_spec.name, task_spec.type) + '\n'
            elif task_spec.is_start():
                dump = '%s (%s-Start)' % (task_spec.name, task_spec.type) + '\n'
            else:
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

        if not self.is_multiple_start:
            dump = recursive_dump(self.start, '')
        else:
            dump = '[Multiple start-task workflow]' + '\n'
            for task in self.start_tasks:
                dump += '' + '\n'
                dump += recursive_dump(self.start_tasks[task], '')

        return dump

    def dump(self, verbose=False):
        print "-------------------------------------------"
        print "Workflow: %s" % self.name
        print self.get_dump(verbose=verbose)
        print "-------------------------------------------"
