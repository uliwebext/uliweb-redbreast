#coding=utf8
from redbreast.core.utils import EventDispatcher
from redbreast.core import WFException
from result import *

class TaskSpec(object):
    task_type = 'Task'
    __supported_config_fields__ = ['default', 'automatic', 'desc']
    __supported_codes__ = ['execute', 'ready', 'transfer', 'choose']
    automatic = False
    default   = False

    def __init__(self, name, **kwargs):
        super(TaskSpec, self).__init__()
        self.name = str(name) #unique in workflow
        self.desc = kwargs.get('desc', '')
        self.automatic = kwargs.get('automatic', self.automatic)
        self.default = kwargs.get('default', self.default)

        self._plugins = kwargs.get('plugins', [])

        self._code_strs = {} #cache config code str
        self._codes = {}     #cache executed function def

        self.data = {}

    def __str__(self):
        return "%s (%s)" % (self.name, self.__class__.__name__)

    def register_plugin(self, plugin):
        self._plugins.append(plugin)

    def unregister_plugin(self, plugin):
        self._plugins.remove(plugin)

    def get_type(self):
        return self.task_type or 'SimpleTask'

    def get_alldata(self):
        return self.data

    def get_data(self, name, default=None):
        return self.data.get(name, default)

    def set_data(self, name, value=None):
        if isinstance(name, dict):
            for key in name:
                self.data[key] = name[key]
        elif isinstance(name, str):
            self.data[name] = value        

    def is_default(self):
        return self.default

    def update_fields(self, data):
        for key in data:
            if key in self.__supported_config_fields__:
                setattr(self, key, data[key])
            else:
                self.set_data(key, data[key])

        self.update_fields_type()

    def update_fields_type(self):
        def convert(val):
            if val == "True" or val == "true" or val == "1":
                return True
            return False
        if not isinstance(self.automatic, bool):
            self.automatic = convert(self.automatic)

        if not isinstance(self.default, bool):
            self.default = convert(self.default)

    def update_codes(self, data):
        fixed_param = "(task, workflow):"
        for key in data:
            update_str = data[key].replace("():", fixed_param, 1)
            self._code_strs[key] = update_str
            scope = {}
            scope = inject_const_scope(scope)
            exec(update_str, scope)
            self._codes[key] = scope[key]    

    def get_code(self, fnc_name):
        key = "%s_%s" % (self.name, fnc_name)
        return self._codes.get(key, None)

    def ready(self, task, workflow):
        fnc_ready = task.spec.get_code('ready') or self.default_ready
        ret = fnc_ready(task, workflow)

        # YES  ACTIVE --> READY
        # NO   nothing
        if ret == YES:
            from redbreast.core import Task
            task.state = Task.READY

            #plugin
            for plugin in self._plugins:
                plugin.state_updated("ready", task=task, workflow=workflow)
        return ret

    def default_ready(self, task, workflow):
        if self.automatic:
            return YES
        else:
            return NO

    def execute(self, task, workflow, transfer=False):
        from redbreast.core import Task
        fnc_execute = task.spec.get_code('execute') or self.default_execute
        ret = fnc_execute(task, workflow)

        # DOING READY -> EXECUTING
        # DONE  READY -> EXECUTED
        # NO    nothing

        if ret == DOING:
            task.state = Task.EXECUTING
            #plugin
            for plugin in self._plugins:
                plugin.state_updated("executing", task=task, workflow=workflow)


        if ret == DONE:
            task.state = Task.EXECUTED
            #plugin
            for plugin in self._plugins:
                plugin.state_updated("executed", task=task, workflow=workflow)
            if transfer:
                return self.transfer(task, workflow)

        return ret

    def default_execute(self, task, workflow):
        return DONE

    def transfer(self, task, workflow):
        from redbreast.core import Task

        fnc_transfer = task.spec.get_code('transfer') or self.default_transfer

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
                #plugin
                for plugin in self._plugins:
                    plugin.state_updated("completed", task=task, workflow=workflow)

                for task_spec in task.spec.outputs:
                    if new_ret == YES or (task_spec.name in new_ret):

                        new_task = workflow.Task(workflow,
                            task_spec, parent=task, operator=task.operator,
                            message=task.deliver_msg)
                        #new_task.add_parent(task)
                        #Test ready for every new added child
                        task_spec.ready(new_task, workflow)
            return ret
        else:
            task.state = Task.COMPLETED
            #plugin
            for plugin in self._plugins:
                plugin.state_updated("completed", task=task, workflow=workflow)

            workflow.finish(finish_task=task)
            return True

    def default_transfer(self, task, workflow):
        return YES

class SimpleTask(TaskSpec):
    task_type = 'SimpleTask'

class SplitTask(TaskSpec):
    task_type = 'SplitTask'
    def default_transfer(self, task, workflow):
        if len(task.spec.outputs)<1:
            raise WFException('No output tasks for choosing.', self)
        ret = self.default_choose(task, workflow)
        return ret

    def default_choose(self, task, workflow):
        return YES

class JoinTask(TaskSpec):
    task_type = 'JoinTask'

    def join_ready(self, task, workflow):
        from redbreast.core import Task

        #merge tasks
        for one in workflow.task_tree:
            if one != task and one.spec == task.spec and one.state & Task.ACTIVE != 0 :
                for p in task.parents:
                    one.add_parent(p)
                    p.add_child(one)

                #TODO
                # data_merget before killed
                # need add a custom method or event to know this merge or doing something

                task.kill()
                one.spec.ready(one, workflow)
                return NO

        #check no uncompleted task in all joined path
        specs = task.spec.get_ancestors()
        for one in workflow.task_tree:
            if one.state & Task.COMPLETED == 0 and one.spec.name in specs:
                return NO

        return YES

    def default_ready(self, task, workflow):
        return self.join_ready(task, workflow)

class ChoiceTask(TaskSpec):
    task_type = 'ChoiceTask'

    def default_transfer(self, task, workflow):
        if len(task.spec.outputs)<1:
            raise WFException(self, 'No output tasks for choosing.')

        fnc_choose = task.spec.get_code('choose') or self.default_choose
        ret = fnc_choose(task, workflow)
        if not isinstance(ret, tuple) and not isinstance(ret, list):
            ret = [ret]

        if len(ret) > 1:
            raise WFException('ChoiceTask %s could choose only one deliver task.' % self.name, self)

        return ret

    def default_choose(self, task, workflow):
        result = []
        next_tasks = task.next_tasks
        output_spec_names = [task_spec.name for task_spec in task.spec.outputs]

        for next_task in next_tasks:
            if not next_task in output_spec_names:
                raise WFException('user choosed task %s is invalid' % next_task.name, self)
            result.append(next_task)

        if len(result) > 0:
            # 1/ user choices in next_tasks
            return result
        else:
            # 2/ default choice in spec
            for task_spec in task.spec.outputs:
                if task_spec.is_default():
                    return [task_spec.name]
            # 3/ first flow in spec
        return [task.spec.outputs[0].name]

class MultiChoiceTask(TaskSpec):
    task_type = 'MultiChoiceTask'

    def default_transfer(self, task, workflow):
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

class AutoSimpleTask(SimpleTask):
    automatic = True

class AutoSplitTask(SplitTask):
    automatic = True

class AutoJoinTask(JoinTask):
    automatic = True

class AutoChoiceTask(ChoiceTask):
    automatic = True

class AutoMultiChoiceTask(MultiChoiceTask):
    automatic = True

class TaskSpecPlugin(object):
    def state_updated(self, state, task=None, workflow=None):
        pass



