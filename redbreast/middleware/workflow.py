from redbreast.core import Workflow, Task

__DEBUG__ = False

class TaskTrans(object):
    CREATE     =  1
    DELIVER    =  2
    ARCHIVE    =  3

    @staticmethod
    def save(from_task, to_task, workflow, message, operator):
        trans_obj = TaskTrans(from_task, to_task, workflow, message, operator)
        trans_obj.serialize()

    @staticmethod
    def remove(from_task, to_task, workflow):
        trans_obj = TaskTrans(from_task, to_task, workflow)
        trans_obj.kill()

    def __init__(self, from_task, to_task, workflow, message, operator):
        self.from_task = from_task
        self.to_task = to_task
        self.workflow = workflow
        self.message = message
        self.operator = operator
        if from_task and to_task:
            self.type = TaskTrans.DELIVER
        elif not from_task:
            self.type = TaskTrans.CREATE
        elif not to_task:
            self.type = TaskTrans.ARCHIVE
        self.obj = None

    def get_serialize_obj(self):
        if not self.obj:
            from uliweb.orm import get_model
            WFTrans = get_model('workflow_trans')
            cond = WFTrans.c.workflow == self.workflow.get_id()
            if self.from_task:
                cond = (WFTrans.c.from_task == self.from_task.get_id()) & cond
            else:
                cond = (WFTrans.c.from_task == None) & cond
            if self.to_task:
                cond = (WFTrans.c.to_task == self.to_task.get_id()) & cond
            else:
                cond = (WFTrans.c.to_task == None) & cond

            obj = WFTrans.get(cond)
            if obj:
                self.obj = obj

        return self.obj

    def serialize(self):
        obj = self.get_serialize_obj()
        if not obj:
            from uliweb.orm import get_model
            WFTrans = get_model('workflow_trans')
            data = {
                'workflow' : self.workflow.get_id(),
                'message'  : self.message,
                'type'     : self.type,
            }

            if self.from_task:
                data.update({
                    'from_task': self.from_task.get_id(),
                    'from_name': self.from_task.get_desc(),
                })

            if self.to_task:
                data.update({
                    'to_task'  : self.to_task.get_id(),
                    'to_name'  : self.to_task.get_desc(),
                })

            if self.operator:
                data.update({'created_user': self.operator})

            obj = WFTrans(**data)
            obj.save()
            self.obj = obj

    def kill(self):
        obj = self.get_serialize_obj()
        if obj:
            obj.delete()

    def get_id(self):
        if self.obj:
            return self.obj.id
        return None

class TaskDB(Task):

    def __init__(self, workflow, task_spec, parent=None, state=Task.ACTIVE, **kwargs):
        self.obj = None
        self.killed = False
        super(TaskDB, self).__init__(workflow, task_spec, parent=parent, state=state, **kwargs)

    def kill(self):
        super(TaskDB, self).kill()
        if self.obj:
            self.obj.delete()
            self.killed = True

    def get_id(self):
        if self.obj:
            return self.obj.id
        return None

    def serialize(self):
        if not self.killed:
            from uliweb.orm import get_model
            WFTask = get_model('workflow_task')

            data = {
                'workflow'      : self.workflow.obj.id,
                'state'         : self.state,
                'spec_name'     : self.get_spec_name(),
                'alias_name'    : self.get_name(),
                'desc'          : self.get_desc(),
                'uuid'      : self.uuid,
            }
            if self.obj:
                self.obj.update(**data)
            else:
                self.obj = WFTask(**data)
            self.obj.save()

    def deserialize(self, obj):
        #state
        self.obj = obj
        if self.obj:
            self._state = obj.state
            self.state_history = [obj.state]
            self.uuid = obj.uuid

class WorkflowDB(Workflow):

    @staticmethod
    def load(workflow_id):
        from uliweb.orm import get_model
        from redbreast.core.spec import CoreWFManager
        WF = get_model('workflow')
        obj = WF.get(WF.c.id == workflow_id)
        if obj:
            workflow_spec = CoreWFManager.get_workflow_spec(obj.spec_name)
            instance = WorkflowDB(workflow_spec, deserializing=True)
            instance.deserialize(obj)
            instance.deserializing = False
            return instance
        return None

    def __init__(self, workflow_spec, **kwargs):
        from uliweb.orm import get_model

        super(WorkflowDB, self).__init__(workflow_spec, task_klass=TaskDB, **kwargs)

        self.deserializing = kwargs.get('deserializing', False)
        self.obj = None
        self.model = get_model('workflow')

        def task_save(event):
            if not event.target.deserializing:
                task = event.task
                task.serialize()

        def trans_add(event):
            if not event.target.deserializing:
                TaskTrans.save(event.from_task,
                    event.to_task, event.workflow,
                    event.from_task.deliver_msg,
                    event.from_task.operator)

        def trans_remove(event):
            if not event.target.deserializing:
                TaskTrans.remove(event.from_task, event.to_task, event.workflow)

        self.on("task:state_changed"    , task_save)
        self.on("task:connect"          , trans_add)
        self.on("task:disconnect"       , trans_remove)

        def workflow_save(event):
            if not event.target.deserializing:
                wf = event.workflow

                if wf.state == Workflow.RUNNING:
                    TaskTrans.save(None, wf.task_tree, wf, None, wf.task_tree.operator)

                if wf.state == Workflow.FINISHED:
                    TaskTrans.save(wf.finish_task, None, wf, wf.finish_task.deliver_msg,
                        wf.finish_task.operator)

                wf.serialize()

        self.on("workflow:state_changed", workflow_save)
        self.on("workflow:data_changed", workflow_save)
        if not self.deserializing:
            self.serialize()

    def get_state_name(self):
        if self.obj:
            return self.obj.get_display_value('state')
        else:
            from uliweb import settings
            choices = settings.get_var('PARA/WF_STATUS')
            return choices[self.state]

    def get_id(self):
        if self.obj:
            return self.obj.id
        return None

    def serialize(self):
        from uliweb.orm import get_model
        from uliweb.utils.common import Serial
        WF = get_model('workflow')

        data = {
            'spec_name'     : self.spec.name,
            'state'         : self.state,
            'data'          : Serial.dump(self.data),
            'desc'          : self.spec.desc,

        }

        #DEBUG -------------------------
        if __DEBUG__:
            for i in data:
                print (i, data[i])

            print 'spec_name: %s' % self.spec.name
            print 'state: %s' % self.state

        #DEBUG
        if self.obj:
            self.obj.update(**data)
        else:
            self.obj = WF(**data)
        self.obj.save()

    def deserialize(self, obj):
        from redbreast.core.spec import CoreWFManager
        from uliweb.orm import get_model
        from uliweb.utils.common import Serial
        WFTask = get_model('workflow_task')
        WFTrans = get_model('workflow_trans')

        self.obj = obj
        if obj:
            workflow_spec = CoreWFManager.get_workflow_spec(obj.spec_name)
            self.spec = workflow_spec
            self.state = obj.state
            self.data = Serial.load(obj.data)

            start_task_obj = None
            task_list = {}

            for task_obj in obj.tasks.order_by(WFTask.c.id):
                if not start_task_obj:
                    start_task_obj = task_obj
                task_list[task_obj.id] = self.Task(
                    self, self.spec.get_task_spec(task_obj.alias_name), state=None)
                task_list[task_obj.id].deserialize(task_obj)

            #DEBUG -------------------------
            if __DEBUG__:
                for a in task_list:
                    print a, task_list[a]
                print "----------------------------------------------"
                print task_list[start_task_obj.id]
                print "----------------------------------------------"
            #DEBUG -------------------------

            self.task_tree = task_list[start_task_obj.id]

            for trans_obj in obj.trans.order_by(WFTrans.c.id):
                from_task_id = trans_obj._from_task_
                to_task_id = trans_obj._to_task_
                if from_task_id and to_task_id:
                    task_list[from_task_id].children.append(task_list[to_task_id])
                    task_list[to_task_id].parents.append(task_list[from_task_id])
