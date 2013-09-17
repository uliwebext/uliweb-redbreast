from redbreast.core.spec import parse, parseFile

class WFStorage(object):
    def load_workflow(self, wf_spec_name):
        raise NotImplementedError

class WFConfigStorage(object):
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
        
