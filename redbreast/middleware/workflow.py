from redbreast.core import Workflow, Task

class TaskTrans(object):
    
    def __init__(self, from_task, to_task, workflow):
        self.from_task = from_task
        self.to_task = to_task
        self.workflow = workflow
        self.obj = None
        
    def get_serialize_obj(self):
        if not self.obj:
            from uliweb.orm import get_model
            WFTrans = get_model('workflow_trans')
            cond = WFTrans.c.workflow == self.workflow.get_id()
            cond = (WFTrans.c.from_task == self.from_task.get_id()) & cond
            cond = (WFTrans.c.to_task == self.to_task.get_id()) & cond
            
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
                'from_task': self.from_task.get_id(),
                'to_task'  : self.to_task.get_id(),
                'from_name': self.from_task.get_name(),
                'to_name'  : self.to_task.get_name(),
            }
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
    
    def __init__(self, workflow, task_spec, parent=None, state=Task.WAITING):
        self.obj = None
        self.killed = False
        super(TaskDB, self).__init__(workflow, task_spec, parent, state)
        
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
                'workflow': self.workflow.obj.id,
                'state': self.state,
                'spec_name': self.get_spec_name(),
                'alias_name': self.get_name()
            }
            if self.obj:
                self.obj.update(**data)
            else:
                self.obj = WFTask(**data)
            self.obj.save()
        
        
            

class WorkflowDB(Workflow):
    
    def __init__(self, workflow_spec, **kwargs):
        super(WorkflowDB, self).__init__(workflow_spec, task_klass=TaskDB, **kwargs)
        self.obj = None
        
        def task_save(event):   
            task = event.task
            task.serialize()
            
        def trans_add(event):
            from_task = event.from_task
            to_task = event.to_task
            workflow = event.workflow
            trans = TaskTrans(from_task, to_task, workflow)
            trans.serialize()
            
        def trans_remove(event):
            from_task = event.from_task
            to_task = event.to_task
            workflow = event.workflow
            trans = TaskTrans(from_task, to_task, workflow)
            trans.kill()

        self.on("state_changed", task_save)
        self.on("trans:add", trans_add)
        self.on("trans:remove", trans_remove)
        
        def workflow_save(event):
            wf = event.workflow
            wf.serialize()
            
        self.on("workflow:state_changed", workflow_save)
        self.serialize()
        
    def get_id(self):
        if self.obj:
            return self.obj.id
        return None
    
    def serialize(self):
        from uliweb.orm import get_model
        WF = get_model('workflow')
        
        data = {
            'spec_name': self.spec.name,
            'state': self.state,
        }
        if self.obj:
            self.obj.update(**data)
        else:
            self.obj = WF(**data)
        self.obj.save()
        

