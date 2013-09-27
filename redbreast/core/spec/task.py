#coding=utf8
from redbreast.core.utils import EventDispatcher
from redbreast.core.exception import WFException
from redbreast.core.const import WFConst
from result import *


class TaskSpec(object):
    task_type = 'Task'
    __supported_config_fields__ = ['default']
    __supported_codes__ = []
    
    def __init__(self, name, **kwargs):
        super(TaskSpec, self).__init__()
        self.name = str(name) #unique in workflow
        self.desc = kwargs.get('desc', '')
        self.default = kwargs.get('default', False)
        
    def __str__(self):
        return "%s (%s)" % (self.name, self.__class__.__name__)
    
    def get_type(self):
        return self.task_type or 'SimpleTask'
    
    def is_default(self):
        return self.default
    
    def update_fields(self, data):
        for key in data:
            if key in self.__supported_config_fields__:
                setattr(self, key, data[key])
    
    def update_codes(self, data):
        for key in data:
            if key in self.__supported_codes__:
                self._code_strs[key] = data[key]
                
    def is_ready(self, task, workflow):
        fnc_ready = task.spec.get_code('ready') or self.ready
        ret = fnc_ready(task, workflow)
        
        # YES  WAITING --> READY
        # NO   nothing
        if ret == YES:
            from redbreast.core import Task
            task.state = Task.READY
            #pubsub
            workflow.spec.fire(WFConst.EVENT_TASK_READY,
                task=task, workflow=workflow)
        return ret
    
    def ready(self, task, workflow):
        return YES
        
    def do_execute(self, task, workflow, transfer=False):
        from redbreast.core import Task
        fnc_execute = task.spec.get_code('execute') or self.execute
        ret = fnc_execute(task, workflow)
        
        # DOING READY -> EXECUTING
        # DONE  READY -> EXECUTED
        # NO    nothing
        
        if ret == DOING:
            task.state = Task.EXECUTING
            #pubsub
            workflow.spec.fire(WFConst.EVENT_TASK_EXECUTING,
                task=task, workflow=workflow)
                
        if ret == DONE:
            task.state = Task.EXECUTED
            #pubsub
            workflow.spec.fire(WFConst.EVENT_TASK_EXECUTED,
                task=task, workflow=workflow)
            if transfer:
                return self.do_transfer(task, workflow)
                
        return ret
    
    def execute(self, task, workflow):
        return DONE
        
    def do_transfer(self, task, workflow):
        from redbreast.core import Task
        
        fnc_transfer = task.spec.get_code('execute') or self.transfer
        
        # TASK      EXECUTED --> COMPLETED
        # YES       EXECUTED --> COMPLETED
        # NO        nothing
        
        if len(task.spec.outputs)>0:
            ret = fnc_transfer(task, workflow)
            if ret != NO:
                
                if isinstance(ret, tuple) or isinstance(ret, list):
                    new_ret = TASK.union(ret)
                else:
                    new_ret = ret
                    
                task.state = Task.COMPLETED
                #pubsub
                workflow.spec.fire(WFConst.EVENT_TASK_COMPLETED,
                    task=task, workflow=workflow)
                
                for task_spec in task.spec.outputs:
                    if new_ret == YES or (task_spec.name in new_ret):
                        new_task = Task(workflow, task_spec, parent=task)
                        #Test ready for every new added child
                        task_spec.is_ready(new_task, workflow)
            return ret
        else:
            #MYTODO: finish workkflow
            return True
    
    def transfer(self, task, workflow):
        return YES

class SimpleTask(TaskSpec):
    task_type = 'SimpleTask'
    
class SplitTask(TaskSpec):
    task_type = 'SplitTask'
    def transfer(self, task, workflow):
        if len(task.spec.outputs)<1:
            raise WFException(self, 'No output tasks for choosing.')
        ret = self.choose(workflow.get_alldata(), task, workflow)
        return ret
        
    def choose(self, data, task, workflow):
        return YES
    
class JoinTask(TaskSpec):
    task_type = 'JoinTask'
    
    def ready(self, task, workflow):
        #check no uncompleted task in all joined path
        
        
        
        return False
    
class ChoiceTask(TaskSpec):
    task_type = 'ChoiceTask'
    
    def transfer(self, task, workflow):
        if len(task.spec.outputs)<1:
            raise WFException(self, 'No output tasks for choosing.')
        ret = self.choose(workflow.get_alldata(), task, workflow)
        return ret
        
    def choose(self, data, task, workflow):
        for task_spec in task.spec.outputs:
            if task_spec.is_default():
                return [task_spec.name]
        return [task.spec.outputs[0].name]
    
class MultiChoiceTask(TaskSpec):
    task_type = 'MultiChoiceTask'    
    
    def transfer(self, task, workflow):
        if len(task.spec.outputs)<1:
            raise WFException(self, 'No output tasks for choosing.')
        ret = self.choose(workflow.get_alldata(), task, workflow)
        return ret
        
    def choose(self, data, task, workflow):
        default_tasks = []
        for task_spec in task.spec.outputs:
            if task_spec.is_default():
                default_tasks.append(task_spec.name)
        if default_tasks:
            return defalut_tasks
        return []
    
    
    
    
