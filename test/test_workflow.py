from redbreast.core.spec import CoreWFManager
from redbreast.core.spec import *
from redbreast.core import Workflow, Task
from os.path import dirname, join

class TestWorkflow(object):
    
    def setup(self):
        CoreWFManager.reset()
        storage = WFConfigStorage()
        CoreWFManager.set_storage(storage)

        config_file = join(dirname(__file__), "data/TestWorkflow.config")
        storage.load_config_file(config_file)

    def test_workflow(self):
        
        workflow_spec = CoreWFManager.get_workflow_spec('TestWorkflow')
        workflow = Workflow(workflow_spec)
        
