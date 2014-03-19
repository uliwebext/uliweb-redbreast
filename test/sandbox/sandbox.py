from redbreast.core.spec import CoreWFManager
from redbreast.core.spec import *
from redbreast.core import Workflow, Task
from os.path import dirname, join

def event_log(event):
    print " --> spec %s, %s" % (event.task.get_name(), event.type)

CoreWFManager.reset()
storage = WFConfigStorage()
CoreWFManager.set_storage(storage)

config_file = join(dirname(__file__), "data/Sandbox2.config")
storage.load_config_file(config_file)

workflow_spec = CoreWFManager.get_workflow_spec('TestWorkflow')
#workflow_spec.on("ready", event_log)
workflow_spec.on("executed", event_log)
#workflow_spec.on("completed", event_log)

print "--------Workflow Spec Dump ----------------------"
workflow_spec.dump()

workflow = Workflow(workflow_spec)
print "---------START-------------------"
workflow.start()
workflow.run()
print "---------RUN-------------------"
workflow.task_tree.dump()
        
