from redbreast.core import Workflow, Task


class TaskDB(Task):
    pass

class WorkflowDB(Workflow):
    
    def __init__(self, workflow_spec, **kwargs):
        super(WorkflowDB, self).__init__(workflow_spec, task_klass=TaskDB, **kwargs)

