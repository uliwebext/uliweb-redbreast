from redbreast.core.spec import SimpleTask, SplitTask, JoinTask
from redbreast.core.spec import ChoiceTask, MultiChoiceTask
from redbreast.core.spec import TaskSpecPlugin

class DatabasePlugin(TaskSpecPlugin):
    def __init__(self):
        super(DatabasePlugin, self).__init__()
        self.task_id = None
        
    def state_updated(self, state, task=None, workflow=None):
        super(DatabasePlugin, self).state_updated(state, task, workflow)
        print "......task %s..................state: %s " % (task.get_name(), state)

class SimpleTaskDB(SimpleTask):
    def __init__(self, name, **kwargs):
        super(SimpleTaskDB, self).__init__(name, **kwargs)
        self.register_plugin(DatabasePlugin())

class SplitTaskDB(SplitTask):
    def __init__(self, name, **kwargs):
        super(SplitTaskDB, self).__init__(name, **kwargs)
        self.register_plugin(DatabasePlugin())

class JoinTaskDB(JoinTask):
    def __init__(self, name, **kwargs):
        super(JoinTaskDB, self).__init__(name, **kwargs)
        self.register_plugin(DatabasePlugin())

class ChoiceTaskDB(ChoiceTask):
    def __init__(self, name, **kwargs):
        super(ChoiceTaskDB, self).__init__(name, **kwargs)
        self.register_plugin(DatabasePlugin())

class MultiChoiceTaskDB(MultiChoiceTask):
    def __init__(self, name, **kwargs):
        super(MultiChoiceTaskDB, self).__init__(name, **kwargs)
        self.register_plugin(DatabasePlugin())
