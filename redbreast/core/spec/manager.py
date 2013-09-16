from redbreast.core.utils import Singleton

class WFManager(object):
    __metaclass__ = Singleton  

    def __init__(self):
        self.wf_specs = {}
        self.task_specs = {}
        self.storage = None
        
    def reset(self):
        self.wf_specs = {}
        self.task_specs = {}
        
    def get_workflow_spec(self, wf_spec_name):
        if not wf_spec_name in self.wf_specs:
            self.load_workflow(wf_spec_name)
        return self.wf_specs.get(wf_spec_name, None)
    
    def get_task_spec(self, task_spec_name):
        
        from redbreast.core.spec import StartTask
        from redbreast.core import WFConst
        
        spec = self.task_specs.get(task_spec_name, None)
        if not spec:
            if task_spec_name == WFConst.TASK_START:
                spec = StartTask()
                self.add_task_spec(spec)
                return spec
    
    def load_workflow(self, wf_spec_name):
        if wf_spec_name in self.wf_specs:
            return self.wf_specs[wf_spec_name]
        else:
            if self.storage:
                proc, tasks = self.storage.load_workflow(wf_spec_name)
            
                #instance 
                for task in tasks:
                    if task in self.task_specs:
                        pass #raise Error
                    else:
                        task_spec = None
                        
                        
                        
                        
                return self.wf_specs[wf_spec_name]
            return None
    
    def add_workflow_spec(self, wf_spec):
        if wf_spec.name in self.wf_specs:
            raise KeyError('Duplicate worlflow spec name: ' + wf_spec.name)
        self.wf_specs[wf_spec.name] = wf_spec
        
    def add_task_spec(self, task_spec):
        if task_spec.name in self.task_specs:
            raise KeyError('Duplicate task spec name: ' + task_spec.name)
        self.task_specs[task_spec.name] = task_spec
        
    def set_storage(self, storage):
        self.storage = storage
        
CoreWFManager = WFManager()        
