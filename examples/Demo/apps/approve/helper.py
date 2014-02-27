
from redbreast.core.spec import CoreWFManager
from redbreast.middleware import Workflow, Task

class ApproveHelper(object):

    def __init__(self):
        self.init_workflow_engine()
        self.WORKFLOW_NAME = "ApproveWorkflow"

        self._approve = None
        self._workflow = None

    def bind(self, approve, get_workflow=False):
        self._approve = approve

        if get_workflow and self._approve.workflow:
            if not self._workflow:
                self._workflow = Workflow.load(self._approve._workflow_)

    def init_workflow_engine(self):
        CoreWFManager.use_database_storage()

    def create_workflow(self, start=True):
        spec = CoreWFManager.get_workflow_spec(self.WORKFLOW_NAME)
        workflow = Workflow(spec)

        workflow.set_data({'table': 'approve', 'obj_id': self._approve.id})

        if start:
            workflow.start()

        self._approve.workflow = workflow.get_id()
        self._approve.save()

        return workflow

    def get_workflow_state(self):
        if self._workflow:
            return self._workflow.get_state_name()
        return ""

    def get_workflow_tasklog(self):
        pass

    def get_translog(self):
        pass

