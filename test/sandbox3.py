from redbreast.core.spec import CoreWFManager
from redbreast.core.spec import *
from redbreast.core import Workflow, Task
import os
from os.path import dirname, join

def event_log(event):
    print " --> spec %s, %s" % (event.task.get_name(), event.type)

locate_dir = os.path.dirname(__file__)
os.chdir(locate_dir)
os.chdir('test_project')
from uliweb.manage import make_simple_application
app = make_simple_application(apps_dir='./apps')

CoreWFManager.reset()
storage = WFDatabaseStorage()
CoreWFManager.set_storage(storage)

workflow_spec = CoreWFManager.get_workflow_spec('TestWorkflow')
#workflow_spec.on(WFConst.EVENT_TASK_READY, event_log)
workflow_spec.on(WFConst.EVENT_TASK_EXECUTED, event_log)
#workflow_spec.on(WFConst.EVENT_TASK_COMPLETED, event_log)

print "--------Workflow Spec Dump ----------------------"
workflow_spec.dump()

workflow = Workflow(workflow_spec)
print "---------START-------------------"
workflow.start()
workflow.run()
print "---------RUN-------------------"
workflow.task_tree.dump()
        
