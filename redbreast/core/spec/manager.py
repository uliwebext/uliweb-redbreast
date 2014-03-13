from redbreast.core.utils import Singleton, CommonUtils
from redbreast.core import WFException
from flow import WorkflowSpec

class WFManager(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.wf_specs = {}
        self.task_specs = {}
        # use WFSpecFileStorage as default storage
        from storage import WFSpecFileStorage
        self.storage = WFSpecFileStorage()
        self._plugins = []

    def register_plugin(self, plugin):
        self._plugins.append(plugin)

    def unregister_plugin(self, plugin):
        self._plugins.remove(plugin)

    def reset(self):
        self.wf_specs = {}
        self.task_specs = {}

    def workflow_spec_is_loaded(self, wf_spec_name):
        return wf_spec_name in self.wf_specs

    def get_workflow_spec(self, wf_spec_name):
        if not wf_spec_name in self.wf_specs:
            self.load_workflow(wf_spec_name)
        return self.wf_specs.get(wf_spec_name, None)

    def get_task_spec(self, task_spec_name):
        spec = self.task_specs.get(task_spec_name, None)
        return spec

    def load_workflow(self, wf_spec_name):
        if wf_spec_name in self.wf_specs:
            return self.wf_specs[wf_spec_name]
        else:
            if self.storage:
                proc, tasks = self.storage.load_workflow(wf_spec_name)

                #instance workflow
                workflow_spec = WorkflowSpec(name=proc['name'], desc=proc.get('desc', proc['name']))

                for name in proc['tasks']:
                    task_spec_name = proc['tasks'][name]
                    task_spec = self.get_task_spec(task_spec_name)

                    #instance used task
                    if not task_spec:
                        task = tasks[name]

                        if not task.has_key('class'):
                            klass = 'AutoSimpleTask'
                        else:
                            klass = task['class']
                            
                        cls = CommonUtils.get_spec(klass)
                        task_spec = cls(task['name'], desc=task.get('desc', task['name']))
                        task_spec.update_fields(task)
                        task_spec.update_codes(task['codes'])
                        self.add_task_spec(task_spec)
                        task_spec = self.get_task_spec(task_spec_name)

                    workflow_spec.add_task_spec(name, task_spec)

                for from_task, to_task in proc['flows']:
                    workflow_spec.add_flow(from_task, to_task)

                workflow_spec.refresh_flow_type()

                workflow_spec.update_fields(proc)
                workflow_spec.update_codes(proc['codes'])

                self.add_workflow_spec(workflow_spec)

                return self.wf_specs[wf_spec_name]
            raise WFException('The workflow %s is not existed.' % wf_spec_name)

    def add_workflow_spec(self, wf_spec):
        if wf_spec.name in self.wf_specs:
            raise KeyError('Duplicate workflow spec name: ' + wf_spec.name)

        #plugin
        for plugin in self._plugins:
            plugin.workflow_spec_added(name=wf_spec.name, spec=wf_spec)

        self.wf_specs[wf_spec.name] = wf_spec

    def add_task_spec(self, task_spec):
        if task_spec.name in self.task_specs:
            raise KeyError('Duplicate task spec name: ' + task_spec.name)

        #plugin
        for plugin in self._plugins:
            plugin.task_spec_added(name=task_spec.name, spec=task_spec)

        self.task_specs[task_spec.name] = task_spec

    def set_storage(self, storage):
        self.storage = storage

    def use_database_storage(self):
        if not self.storage or self.storage.storage_type != "database":
            from storage import WFDatabaseStorage
            self.storage = WFDatabaseStorage()

class WFManagerPlugin(object):
    def workflow_spec_added(self, name=None, spec=None):
        raise NotImplementedError

    def task_spec_added(self, name=None, spec=None):
        raise NotImplementedError

class WFManagerBindPlugin(WFManagerPlugin):

    def __init__(self, binds=[]):
        self.spec = {}

    def bind(self, wf_spec_name, event, handler):
        if not self.spec.has_key(wf_spec_name):
            self.spec[wf_spec_name] = []
        self.spec[wf_spec_name].append((event, handler))

    def workflow_spec_added(self, name=None, spec=None):
        import re
        for spec_name in self.spec.keys():
            regex = "^" + spec_name.replace("*", ".*").replace("?", ".") + "$"
            if (spec_name == "*") or (spec_name == name) or re.complie(regex).search(spec_name):
                for event, handler in self.spec[spec_name]:
                    spec.on(event, handler)

    def task_spec_added(self, name=None, spec=None):
        pass #nothing

CoreWFManager = WFManager()