
from redbreast.middleware import Workflow, Task

WORKFLOW_SPEC_NAME = "ApproveWorkflow"

class ApproveHelper(object):

    def __init__(self):
        from uliweb import request
        self.WORKFLOW_NAME = "ApproveWorkflow"

        self._approve = None
        self._workflow = None
        self.operator = request.user

    def bind(self, approve, get_workflow=False):
        self._approve = approve

        if get_workflow and self._approve.workflow:
            if not self._workflow:

                workflow_id = self._approve._workflow_

                #restore workflow from database
                self._workflow = Workflow.load(workflow_id, operator=self.operator)

    def create_workflow(self, start=True):
        #create new workflow
        workflow = Workflow.create(WORKFLOW_SPEC_NAME, operator=self.operator)
        workflow.set_data({'table': 'approve', 'obj_id': self._approve.id})

        if start:
            workflow.start()

        self._approve.workflow = workflow.get_id()
        self._approve.save()

        return workflow

    def get_workflow(self):
        return self._workflow

    def deliver(self, message, next_tasks=[]):
        if self._workflow and self._current_task:
            async = True
            return self._workflow.deliver(self._current_task.uuid,
                message=message, next_tasks=next_tasks, async=async)


    def get_active_tasks(self):
        tasks = self._workflow.get_active_tasks()

        if len(tasks) == 1:
            self._current_task = tasks[0]
        else:
            self._current_task = None
        return tasks

    def has_deliver_permission(self, task, user):
        from uliweb import settings
        from uliweb import functions
        maps = settings.get_var("WORKFLOW/TASK_PERMISSION_MAP")
        key = "%s.%s" % (self._workflow.get_spec_name(), task.get_name())
        if key in maps:
            for perm in maps[key]:
                if functions.has_permission(user, perm):
                    return True
        return False

    def get_task_spec_names(self, user):
        from uliweb import request
        spec_names = request.session.get('_task_spec_names_')

        if spec_names:
            return spec_names
        else:
            spec_names = []
            from uliweb import settings
            from uliweb import functions
            maps = settings.get_var("WORKFLOW/TASK_PERMISSION_MAP")
            for key in maps:
                wf_spec_name, task_spec_name = key.split(".")
                for perm in maps[key]:
                    if functions.has_permission(user, perm):
                        spec_names.append(task_spec_name)
            request.session.setdefault('_task_spec_names_', spec_names)
            return spec_names





