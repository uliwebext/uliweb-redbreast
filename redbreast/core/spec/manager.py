class WFManager(object):
    
    def __init__(self):
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
        if not spec and task_spec_name == WFConst.TASK_START:
            spec = StartTask()
            self.add_task_spec(spec)
            return spec
    
    def load_workflow(self, wf_spec_name):
        #TODO, load and instance a workflow_spec from configuration
        pass
    
    def add_workflow_spec(self, wf_spec):
        if wf_spec.name in self.wf_specs:
            raise KeyError('Duplicate worlflow spec name: ' + wf_spec.name)
        self.wf_specs[wf_spec.name] = wf_spec
        
    def add_task_spec(self, task_spec):
        if task_spec.name in self.task_specs:
            raise KeyError('Duplicate task spec name: ' + task_spec.name)
        self.task_specs[task_spec.name] = task_spec
        
WFCoreManager = WFManager()
        
