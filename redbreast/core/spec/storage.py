from redbreast.core.spec import parse, parseFile

class WFStorage(object):
    storage_type = 'error'
    def load_workflow(self, wf_spec_name):
        raise NotImplementedError

class WFSpecFileStorage(object):
    storage_type = 'specs'

    def __init__(self, suffix=".spec", folder=""):
        self._cache_tasks = {}
        self._cache_workflows = {}
        self._spec_path = folder
        self._spec_suffix = suffix

    def set_suffix(self, suffix):
        self._spec_suffix = suffix

    def set_folder(self, folder):
        self._spec_path = folder

    def load_spec_file(self, wf_spec_name):
        from os.path import exists, join
        path = join(self._spec_path, wf_spec_name+self._spec_suffix)
        if exists(path):
            tasks, processes = parseFile(path)
            self._cache_tasks.update(tasks)
            self._cache_workflows.update(processes)

    def load_workflow(self, wf_spec_name):
        if not wf_spec_name in self._cache_workflows:
            self.load_spec_file(wf_spec_name)

        if wf_spec_name in self._cache_workflows:
            proc = self._cache_workflows[wf_spec_name]
            tasks = {}
            for key in proc.get('tasks',[]):
                tasks[key] = self._cache_tasks[proc['tasks'][key]]
            return proc, tasks

        raise KeyError('worlflow spec (%s) does not exist.' % wf_spec_name)

class WFConfigStorage(object):
    storage_type = 'config'
    def __init__(self):
        self._cache_tasks = {}
        self._cache_workflows = {}

    def load_config_file(self, path):
        tasks, processes = parseFile(path)
        self._cache_tasks.update(tasks)
        self._cache_workflows.update(processes)

    def load_config_text(self, text):
        tasks, processes = parse(text)
        self._cache_tasks.update(tasks)
        self._cache_workflows.update(processes)

    def load_workflow(self, wf_spec_name):
        if wf_spec_name in self._cache_workflows:
            proc = self._cache_workflows[wf_spec_name]
            tasks = {}
            for key in proc.get('tasks',[]):
                tasks[key] = self._cache_tasks[proc['tasks'][key]]
            return proc, tasks

        raise KeyError('worlflow spec (%s) does not exist.' % wf_spec_name)

class WFDatabaseStorage(WFStorage):
    storage_type = 'database'
    def load_workflow(self, wf_spec_name):

        from uliweb.orm import get_model
        from uliweb.utils.common import Serial

        WorkflowSpec = get_model('workflow_spec')
        TaskSpec = get_model('task_spec')
        spec = WorkflowSpec.get(WorkflowSpec.c.name == wf_spec_name)
        if not spec:
            raise KeyError('worlflow spec (%s) does not exist.' % wf_spec_name)

        proc = Serial.load(spec.content)
        tasks = {}
        task_list = proc.get('tasks', [])
        for key in task_list:
            task = TaskSpec.get(TaskSpec.c.name == task_list[key])
            tasks[key] = Serial.load(task.content)
        return proc, tasks
