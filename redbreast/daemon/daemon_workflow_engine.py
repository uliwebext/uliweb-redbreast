#coding=utf-8
import sys
import time
from generic import GenericDaemon
from uliweb.orm import get_model

__daemon__ = 'workflow_engine'
__daemon_name__ = "Workflow Engine Daemon"
__daemon_port__ = 4202
__daemon_version__ = 'v0.0.1'


# status
STOPPED  = 'STOPPED'
RUNNING  = 'RUNNING'
PAUSED   = 'PAUSED'


###
# worker 
#  [new] RUNNING
#  cmd:worker stop xxx --> STOPPED

# loader
#  cmd:shutdown --> STOPPED, all workers, STOPPED
#  cmd:pause    --> PAUSED, all workers, PAUSED
#  cmd:resume   --> RUNNING, all workers, RUNNING

__WORKER_NAMES__ = ["Kimi", "Jack", "Alex", "Bob", "Alan", "Penny"]

def get_unique_id():
    from uuid import uuid4
    u = str(uuid4()).split("-")[0]
    return u

class Worker(object):
    def __init__(self, name, status, index):
        self.name = name
        self.status = status
        self.index = index

class WFEngineDaemon(GenericDaemon):

    def __init__(self, **kwargs):
        from gevent.queue import Queue

        super(WFEngineDaemon, self).__init__(**kwargs)
        self.task_model = get_model('workflow_task')

        self.limit = kwargs.get("query_limit", 10)
        self.daemon_id = kwargs.get("daemon_id", get_unique_id())

        #worker
        self.worker_number = kwargs.get("worker", 4)
        self.workers = {}

        self.queue_limit = kwargs.get("queue_size", 10)
        self.queue = Queue(self.queue_limit)

        self.status = None
        self.is_worker_started = False
        self.tid = 0

        self.register_request('pause', usage="Pause to load new task.")
        self.register_request('resume', usage="Resume to load new task.")
        self.register_request('worker', usage="Show worker information.")

        self.register_request('reset', inner=False)

        self.mainLoopCommands = ["start_workers"]

    def get_server_info(self):
        info = []
        info.append("%s" % __daemon_name__)
        info.append("- version: %s" % __daemon_version__)
        info.append("- port: %s" % self.port or __daemon_port__)
        info.append("- instance: %s" % self.daemon_id)
        return info

    def get_worker_name(self, i):
        a, b = i//6+1, i % 6
        name = "%s%d" % (__WORKER_NAMES__[b], a)
        while self.workers.has_key(name):
            a = a + 1
            name = "%s%d" % (__WORKER_NAMES__[b], a)
        return name

    def loader(self):
        import gevent
        while True:
            if self.status == STOPPED:
                break

            if self.status == RUNNING:
                # load task from database or redis

                # load task from database:
                self.load_ready_tasks(self.queue)

                gevent.sleep(0)
            else:
                gevent.sleep(0.5)
        self.prints(">>> Loader is stopped at %s" % self.gettimestamp())
        return

    def worker(self, name, index):
        import gevent
        from random import randint
        work_status = RUNNING

        self.workers[name] = Worker(name, RUNNING, index)

        w = self.workers[name]

        while True:
            if w.status == PAUSED:
                if self.status == RUNNING:
                    w.status == RUNNING                       

            if w.status == RUNNING:
                if not self.queue.empty():
                    task = self.queue.get()
                    self.prints('>>> %s got task %s ' % (name, task[0]))
                    self.async_deliver(task[1])
                else:
                    if self.status == PAUSED:
                        self.prints(">>> %s is paused at %s" % (name, self.gettimestamp()))
                        w.status = PAUSED
            
            if w.status == STOPPED:
                break

            gevent.sleep(0)

        del self.workers[name]
        self.prints(">>> %s is stopped at %s" % (name, self.gettimestamp()))
        self.worker_number = len(self.workers)
        if self.worker_number > 1:
            self.prints(">>> still have %d workers at server." % self.worker_number)
        elif self.worker_number == 1:
            self.prints(">>> only one worker at server." )
        else:
            self.prints(">>> no running worker at server.")

    def load_ready_tasks(self, queue):
        from uliweb.orm import Begin, Commit, Rollback, Reset
        from gevent.queue import Full
        import gevent

        if self.queue.full():
            gevent.sleep(0.3)
            return

        Begin()
        try:
            cond = self.task_model.c.state == 2 # READY
            cond = (self.task_model.c.async_status == 0 or self.task_model.c.async_status == None) & cond
            query = self.task_model.filter(cond)
            query = query.order_by(self.task_model.c.async_deliver_date.asc())
            query = query.limit(self.limit)

            isFull = False
            isEmpty = True
            for item in query:
                self.tid = self.tid + 1
                try:
                    queue.put_nowait([self.tid, item.id])
                    item.update(async_status=1)
                    item.save()
                    isEmpty = False
                except Full:
                    isFull = True
                    break

            Commit()    
            if isEmpty and self.debug:
                self.prints(">>> [DEBUG] No tasks found %s" % self.gettimestamp())

            if isFull:
                gevent.sleep(0.3)

            if isEmpty:
                gevent.sleep(0.3)
        except:
            Rollback()
            import traceback
            traceback.print_exc()

    def startMainLoop1(self):
        self.start_workers()
        self.prints(">>> MainLoop is stoped at %s" % self.gettimestamp())

    def mainLoop(self, cmd=None):
        import gevent 
        if self.mainLoopCommands:
            cmd = self.mainLoopCommands.pop()
            if hasattr(self, "do_%s" % cmd):
                gevent.spawn(getattr(self, "do_%s" % cmd))
        #self.prints("mainLoop ..")

    def do_start_workers(self):
        import gevent
        self.prints(">>> Workers are startting....")
        self.status = RUNNING
        # one loader
        greentlets = [gevent.spawn(self.loader)]

        # some workers
        for i in range(1, self.worker_number+1):
            name = self.get_worker_name(i)
            greentlets.append(gevent.spawn(self.worker, name, i))

        gevent.joinall(greentlets)

    def handle_shutdown(self, req):
        self.prints(">>> Worker stopping....")
        self.status = STOPPED
        return super(WFEngineDaemon, self).handle_shutdown(req)

    def handle_pause(self, req):
        self.status = PAUSED
        self.prints(">>> Loader is paused at %s" % self.gettimestamp())
        return self.create_response(True, "The loader is pausing.")

    def handle_resume(self, req):
        self.status = RUNNING
        return self.create_response(True, "The loader is resuming.")

    def handle_worker(self, req):
        subcmd = req.msg
        data = req.data

        if subcmd == "add":
            import gevent

            if data and data.isdigit():
                addcount = int(data)
            else:
                addcount = 1

            msg = []
            for i in range(1, addcount+1):
                self.worker_number = self.worker_number + 1
                name = self.get_worker_name(self.worker_number)
                greenlet = gevent.spawn(self.worker, name, self.worker_number)
                msg.append("new worker %s added" % name)
            return self.create_response(True, "\n".join(msg))

        if subcmd == "show":
            if data:
                if self.workers.has_key(data):
                    w = self.workers[name]
                    msg = "%10s %10s" % (w.index, w.name, w.status)
                    return self.create_response(True, msg)
                else:
                    return self.create_response(False, "cannot find worker %s" % data)

        if subcmd == "del":
            if data:
                if data == "all":
                    msg = []
                    for name in self.workers:
                        w = self.workers[name]
                        w.status = STOPPED
                        msg.append("worker %s was stopped." % name)

                    return self.create_response(True, "\n".join(msg))

                if self.workers.has_key(data):
                    w = self.workers[data]
                    w.status = STOPPED
                    return self.create_response(True, "worker %s was stopped." % data)
            return self.create_response(False, "cannot find worker %s" % data)

        msg = []
        for name in sorted(self.workers):
            w = self.workers[name]
            msg.append("%10s %10s" % (w.name, w.status))
        
        return self.create_response(True, "\n".join(msg))

    def handle_reset(self, req):
        Task = self.task_model
        count = 0
        for item in Task.filter(Task.c.async_status == 1):
            item.async_status = None
            item.save()
            count = count + 1

        return self.create_response(True, "reset %d tasks in database." % count)

    def async_deliver(self, task_id):
        from redbreast.serializable import Workflow, Task
        task_obj = self.task_model.get(task_id)
        if task_obj.state == 2: #READY
            wf_id = task_obj._workflow_

            workflow = Workflow.load(wf_id, operator=task_obj._modified_user_)
            task = workflow.get_task(task_obj.uuid)
            self.prints("------------------------------------------------")
            self.prints("spec %s %s(%s)" % (workflow.get_spec_name(), task.get_name(), task.get_spec_name()))
            message = task.deliver_msg
            next_tasks = task.next_tasks
            workflow.deliver(task_obj.uuid, message=message, next_tasks=next_tasks, async=False)

            task_obj.update(async_status=0)
            task_obj.save()


def start(args, options, global_options, fileconfig):

    kwargs = {'port': __daemon_port__ }
    if fileconfig:
        for key in fileconfig.GLOBAL.keys():
            kwargs[key] = fileconfig.GLOBAL[key]

    if options.port:
        kwargs['port'] = options.port

    daemon = WFEngineDaemon(**kwargs)
    daemon.start()

if __name__ == '__main__':
    async_loop()
