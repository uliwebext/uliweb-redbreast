#coding=utf-8
import sys
import time
from generic import GenericDaemon
from uliweb.orm import get_model
import logging

LOG = logging.getLogger("redbreast.daemon")

__daemon__ = 'workflow_engine'
__daemon_name__ = "Workflow Engine Daemon - redbreast"
__daemon_port__ = 4202
__daemon_version__ = 'v0.0.1'

class WFEngineDaemon(GenericDaemon):
    def __init__(self, **kwargs):
        super(WFEngineDaemon, self).__init__(**kwargs)
        self.task_model = get_model('workflow_task')
        self.limit = 10


    def get_server_info(self):
        info = []
        info.append("%s" % __daemon_name__)
        info.append("- version: %s" % __daemon_version__)
        info.append("- port: %s" % __daemon_port__)
        return info

    def mainLoop(self):
        from uliweb.orm import Begin, Commit, Rollback, Reset

        Begin()
        try:
            cond = self.task_model.c.state == 2 # READY
            query = self.task_model.filter(cond)
            query = query.order_by(self.task_model.c.async_deliver_date.asc())
            query = query.limit(self.limit)

            for item in query:
                self.async_deliver(item)
            Commit()
        except:
            Rollback()
            import traceback
            traceback.print_exc()

    def async_deliver(self, task_obj):
        from redbreast.serializable import Workflow, Task
        wf_id = task_obj.workflow.id

        workflow = Workflow.load(wf_id, operator=task_obj._modified_user_)
        task = workflow.get_task(task_obj.uuid)
        LOG.info("------------------------------------------------")
        LOG.info("spec %s %s(%s)" % (workflow.get_spec_name(), task.get_name(), task.get_spec_name()))
        message = task.deliver_msg
        next_tasks = task.next_tasks
        workflow.deliver(task_obj.uuid, message=message, next_tasks=next_tasks, async=False)


def start(args, options, global_options):
    port = options.port and __daemon_port__
    daemon = WFEngineDaemon(port=port)
    daemon.start()

if __name__ == '__main__':
    async_loop()
