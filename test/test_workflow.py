from redbreast.core.spec import CoreWFManager
from redbreast.core.spec import *
from redbreast.core import Workflow, Task
from os.path import dirname, join

class TestWorkflow(object):
    
    def setup(self):
        
        spec_dir = "test_project/apps/specapp/workflow_specs/"
        
        CoreWFManager.reset()
        storage = WFConfigStorage()
        CoreWFManager.set_storage(storage)

        config_file = join(dirname(__file__), spec_dir + "TestWorkflow.spec")
        storage.load_config_file(config_file)

    def test_workflow(self):
        
        workflow_spec = CoreWFManager.get_workflow_spec('TestWorkflow')
        workflow = Workflow(workflow_spec)
        
        def event_log(event):
            print "Event ... %s " % event.type
            print " .... spec %s" % event.task.get_name()
        
        workflow_spec.on("ready", event_log)
        workflow_spec.on("executed", event_log)
        workflow_spec.on("completed", event_log)
        
        workflow.start()
        
if __name__ == '__main__':
    test = TestWorkflow()
    test.setup()
    test.test_workflow()
        
        
