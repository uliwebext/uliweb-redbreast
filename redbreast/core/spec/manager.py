from redbreast.core.utils import Singleton, CommonUtils
from redbreast.core import WFException
from flow import WorkflowSpec

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
        spec = self.task_specs.get(task_spec_name, None)
        return spec
    
    def load_workflow(self, wf_spec_name):
        if wf_spec_name in self.wf_specs:
            return self.wf_specs[wf_spec_name]
        else:
            if self.storage:
                proc, tasks = self.storage.load_workflow(wf_spec_name)

                #instance workflow
                workflow_spec = WorkflowSpec(name=proc['name'])
                
                for name in proc['tasks']:
                    task_spec_name = proc['tasks'][name]
                    task_spec = self.get_task_spec(task_spec_name)
                    
                    #instance used task
                    if not task_spec:
                        task = tasks[name]
                        
                        klass = task['class']
                        cls = CommonUtils.get_spec(task['class'])
                        task_spec = cls(task['name'])
                        task_spec.update_fields(task)
                        self.add_task_spec(task_spec)
                        task_spec = self.get_task_spec(task_spec_name)
                    
                    workflow_spec.add_task_spec(name, task_spec)
                    
                for from_task, to_task in proc['flows']:
                    workflow_spec.add_flow(from_task, to_task)
                    
                workflow_spec.refresh_flow_type()
                    
                workflow_spec.update_fields(proc)
                workflow_spec.update_codes(proc['codes'])
                self.wf_specs[wf_spec_name] = workflow_spec
                
                return self.wf_specs[wf_spec_name]
            raise WFException('The workflow %s is not existed.' % wf_spec_name)
    
    def add_workflow_spec(self, wf_spec):
        if wf_spec.name in self.wf_specs:
            raise KeyError('Duplicate workflow spec name: ' + wf_spec.name)
        self.wf_specs[wf_spec.name] = wf_spec
        
    def add_task_spec(self, task_spec):
        if task_spec.name in self.task_specs:
            raise KeyError('Duplicate task spec name: ' + task_spec.name)
        self.task_specs[task_spec.name] = task_spec
        
    def set_storage(self, storage):
        self.storage = storage
        
CoreWFManager = WFManager()        
