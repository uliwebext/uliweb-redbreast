
def get_approve_obj(id):
    from uliweb.orm import get_model
    Approve = get_model('approve')
    return Approve.get(int(id))

def workflow_task_enter(event):
    from uliweb.orm import get_model

    if hasattr(event, 'workflow'):
        wf = event.workflow
        if not wf.deserializing:
            obj = get_approve_obj(wf.get_data('obj_id'))
            if obj:
                obj.task_spec_desc = event.task.get_desc()
                obj.task_spec_name = event.task.get_name()
                obj.save()





def workflow_running(event):
    if hasattr(event, 'workflow'):
        pass

def workflow_finished(event):
    if hasattr(event, 'workflow'):
        pass