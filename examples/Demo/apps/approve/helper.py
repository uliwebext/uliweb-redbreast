
from redbreast.core.spec import CoreWFManager
from redbreast.middleware import Workflow, Task

class ApproveHelper(object):

	def __init__(self):
		self.init_workflow_engine()
		self.WORKFLOW_NAME = "ApproveWorkflow"

	def bind(self, approve):
		self._approve = approve

	def init_workflow_engine(self):
		CoreWFManager.use_database_storage()

	def create_workflow(self, start=True):
		spec = CoreWFManager.get_workflow_spec(self.WORKFLOW_NAME)
		workflow = Workflow(spec)

		if start:
			workflow.start()

		self._approve.workflow = workflow.get_id()
		self._approve.save()

		return workflow

