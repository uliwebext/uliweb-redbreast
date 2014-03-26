#coding=utf-8
import sys
import time
from generic import GenericDaemon
from uliweb.orm import get_model

__daemon__ = 'workflow_engine'
__daemon_name__ = "Workflow Engine Daemon - redbreast"
__daemon_port__ = 4202
__daemon_version__ = 'v0.0.1'


STOPPED = 1
RUNNING = 2
PAUSING = 3
PAUSED  = 4

class WFEngineDaemon(GenericDaemon):

    def __init__(self, **kwargs):
        from gevent.queue import Queue

        super(WFEngineDaemon, self).__init__(**kwargs)
        self.task_model = get_model('workflow_task')
        self.limit = 10
        self.is_worker_started = False
        self.workers = ["Kimi", "Jack", "Alex", "Robb"]
        self.queue = Queue(10)

        self.status = None
        self.tid = 0

        self.register_request('pause', usage="Pause to load new task.")
        self.register_request('resume', usage="Resume to load new task.")

    def get_server_info(self):
        info = []
        info.append("%s" % __daemon_name__)
        info.append("- version: %s" % __daemon_version__)
        info.append("- port: %s" % __daemon_port__)
        return info

    def loader(self):
        import gevent
        while True:
            if self.status == STOPPED:
                break

            if self.status == PAUSING:
                self.prints(">>> Loader is paused at %s" % self.gettimestamp())
                self.status = PAUSED

            if self.status == RUNNING:
                for i in range(1, 10):
                    self.tid = self.tid + 1
                    self.queue.put([self.tid, None])

                gevent.sleep(0)
            else:
                gevent.sleep(0.5)
        self.prints(">>> Loader is stopped at %s" % self.gettimestamp())
        return

    def worker(self, name):
        import gevent
        from random import randint
        work_status = RUNNING

        while True:
            if not self.queue.empty():
                work_status = RUNNING

                task = self.queue.get()
                self.prints('>>> %s got task %s ' % (name, task[0]))
            else:
                if self.status == PAUSED and work_status == RUNNING:
                    self.prints(">>> %s is paused at %s" % (name, self.gettimestamp()))
                    work_status = PAUSED

                if self.status == STOPPED:
                    break
            gevent.sleep(1)

        self.prints(">>> %s is stopped at %s" % (name, self.gettimestamp()))

    def start_workers(self):
        import gevent
        self.prints(">>> Worker startting....")
        self.status = RUNNING
        greentlets = [gevent.spawn(self.loader)]

        for name in self.workers:
            greentlets.append(gevent.spawn(self.worker, name))

        gevent.joinall(greentlets)

    def stop_worker(self):
        self.prints(">>> Worker stopping....")
        self.status = STOPPED

    def mainLoop(self, stopit=False):
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

    def startMainLoop(self):
        self.start_workers()
        self.prints(">>> MainLoop is stoped at %s" % self.gettimestamp())

    def handle_shutdown(self, req):
        self.stop_worker()
        return super(WFEngineDaemon, self).handle_shutdown(req)

    def handle_pause(self, req):
        self.status = PAUSING
        return self.create_response(True, "The loader is pausing.")

    def handle_resume(self, req):
        self.status = RUNNING
        return self.create_response(True, "The loader is resuming.")

    def async_deliver(self, task_obj):
        from redbreast.serializable import Workflow, Task
        wf_id = task_obj.workflow.id

        workflow = Workflow.load(wf_id, operator=task_obj._modified_user_)
        task = workflow.get_task(task_obj.uuid)
        self.prints("------------------------------------------------")
        self.prints("spec %s %s(%s)" % (workflow.get_spec_name(), task.get_name(), task.get_spec_name()))
        message = task.deliver_msg
        next_tasks = task.next_tasks
        workflow.deliver(task_obj.uuid, message=message, next_tasks=next_tasks, async=False)


def start(args, options, global_options):
    port = options.port and __daemon_port__
    daemon = WFEngineDaemon(port=port)
    daemon.start()

if __name__ == '__main__':
    async_loop()
