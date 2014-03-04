import logging

from redbreast.core import WFException
from redbreast.core.spec import *
from redbreast.core.utils import EventDispatcher
from uuid import uuid4
from task import Task

import time

LOG = logging.getLogger(__name__)

class Workflow(EventDispatcher):

    CREATED   =  1
    RUNNING   =  2
    FINISHED  =  4

    state_names = {
        CREATED:   'CREATED',
        RUNNING:   'RUNNING',
        FINISHED:  'FINISHED',
    }

    @classmethod
    def create(klass, wf_spec_name, **kwargs):
        from redbreast.core.spec import CoreWFManager
        spec = CoreWFManager.get_workflow_spec(wf_spec_name)
        return klass(spec, **kwargs)

    def __init__(self, workflow_spec, **kwargs):

        LOG.debug("__init__ Workflow instance %s" % str(self))

        super(Workflow, self).__init__()

        self.spec = workflow_spec
        self.Task = kwargs.get('task_klass', Task)
        self.data = {}
        self.parent_workflow = kwargs.get('parent', self)


        self.task_tree = None     #start-task
        self.finish_task = None   #end-task
        self.last_task = None

        self.state = self.CREATED
        self.operator = kwargs.get("operator", None)

        #pubsub
        if self.spec :
            self.spec.fire("workflow:created", workflow=self)
        self.fire("workflow:state_changed", workflow=self)

    def get_alldata(self):
        return self.data

    def get_data(self, name, default=None):
        return self.data.get(name, default)

    def set_data(self, name, value=None):
        if isinstance(name, dict):
            for key in name:
                self.data[key] = name[key]
        elif isinstance(name, str):
            self.data[name] = value
        self.fire("workflow:data_changed", workflow=self)

    def get_spec_name(self):
        return self.spec.name

    def get_state_name(self):
        return self.state_names.get(self.state, None)

    def is_multiple_start(self):
        return self.spec.is_multiple_start

    def start(self, start=None):
        #multipe start tasks
        if self.spec.is_multiple_start:
            if not start :
                raise WFException('You must choose which task to start for mulitple-starts workflow')

            start_task = self.spec.get_task_spec(start)
            if not start_task:
                names = ','.join(self.spec.get_start_names())
                raise WFException('The node you picked up does not exists in [%s]' % (names))
            self.task_tree = self.Task(self, start_task, operator=self.operator)
        else:
            self.task_tree = self.Task(self, self.spec.start, operator=self.operator)

        self.state = self.RUNNING
        #pubsub
        self.spec.fire("workflow:running", workflow=self)
        self.fire("workflow:state_changed", workflow=self)
        self.task_tree.is_ready()

    def run(self):
        while self.run_next():
            pass

    def run_all(self):
        self.run()

    def run_next(self):
        # Walk through all waiting tasks.
        for task in Task.Iterator(self.task_tree, Task.READY):
            #task.task_spec._update_state(task)
            if task._getstate() == Task.READY:
                self.last_task = task
                task.do_execute(transfer=True)
                return True
        return False

    def run_from_id(self, task_id):
        if task_id is None:
            raise WFException(self.spec, 'task_id is None')
        for task in self.task_tree:
            if task.uuid == task_id:
                return task.complete()
        msg = 'A task with the given task_id (%s) was not found' % task_id
        raise WFException(self.spec, msg)

    def deliver(self, task_id, message=None, next_tasks=[], async=True):
        if task_id is None:
            raise WFException(self.spec, 'task_id is None')
        for task in self.task_tree:
            if task.uuid == task_id:
                return task.deliver(message=message, next_tasks=next_tasks, async=async)
        msg = 'A task with the given task_id (%s) was not found' % task_id
        raise WFException(self.spec, msg)

    def get_active_tasks(self):
        return [task for task in Task.Iterator(self.task_tree, Task.ACTIVE)]

    def finish(self, finish_task):
        self.state = self.FINISHED
        self.finish_task = finish_task
        #pubsub
        self.spec.fire("workflow:finished", workflow=self)
        self.fire("workflow:state_changed", workflow=self)
