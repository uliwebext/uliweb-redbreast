import os
from optparse import make_option
from uliweb.core.commands import Command, get_input, get_answer
from uliweb.core.template import template_file


def clear():
    from uliweb.orm import get_model
    WorkflowSpec = get_model('workflow_spec')
    TaskSpec = get_model('task_spec')
    print "Deleting Workflow_Spec ..."
    WorkflowSpec.remove()
    print "Deleting Task_Spec  ..."
    TaskSpec.remove()
    
def loadspec(apps_list):
    from uliweb.core.SimpleFrame import get_app_dir
    from uliweb import settings
    from redbreast.core.spec import parse, parseFile
    
    SPEC_DIR = settings.GLOBAL.SPEC_DIR
    SPEC_SUFFIX = settings.GLOBAL.SPEC_SUFFIX
    
    all_tasks = {}
    all_workflows = {}
    
    for p in apps_list:
        spec_dir =os.path.join(get_app_dir(p), SPEC_DIR)
        if os.path.isdir(spec_dir):
            for f in os.listdir(spec_dir):
                if f.endswith(SPEC_SUFFIX):
                    file = os.path.join(spec_dir, f)
                    print "Parsing file %s ...." % file
                    tasks, processes = parseFile(file)
                    print "  tasks, %s, %s" % (len(tasks), [t for t in tasks])
                    print "  workflow, %s, %s" % (len(processes), [t for t in processes])
                    
                    all_tasks.update(tasks)
                    all_workflows.update(processes)
                    
    return all_tasks, all_workflows
                    

class ClearSpecCommand(Command):
    name = 'clearspec'
    help = 'delete all workflow specs from database.'
    check_apps = True
    
    def handle(self, options, global_options, *args):
        message = """This command will delete all workflow specs, are you sure to do?"""
        get_answer(message)
        self.get_application(global_options)
        clear()
    
class SyncSpecCommand(Command):
    name = 'syncspec'
    
    def handle(self, options, global_options, *args):
        
        apps_list = self.get_apps(global_options)
        loadspec(apps_list)
        
class ShowSpecCommand(Command):
    name = 'showspec'
    
    def handle(self, options, global_options, *args):
        from uliweb.orm import get_model
        from uliweb.utils.common import Serial
        import pprint
        
        self.get_application(global_options)
        WorkflowSpec = get_model('workflow_spec')
        TaskSpec = get_model('task_spec')
        
        print "TaskSpec : "
        for task in TaskSpec.all():
            print " * %s" % task.name
            pprint.pprint(Serial.load(task.content))
        
        print "WorkflowSpec : "
        for wf in WorkflowSpec.all():
            print " * %s" % wf.name
            pprint.pprint(Serial.load(wf.content))

class ReloadSpecCommand(Command):
    name = 'reloadspec'
    
    def handle(self, options, global_options, *args):
        from uliweb.orm import get_model
        from uliweb.core.SimpleFrame import get_app_dir
        
        message = """This command will delete all workflow specs, are you sure to do?"""
        get_answer(message)

        self.get_application(global_options)
        clear()
        print ""
        
        apps_list = self.get_apps(global_options)
        tasks, workflows = loadspec(apps_list)
        
        from uliweb.orm import get_model
        from uliweb.utils.common import Serial
        WorkflowSpec = get_model('workflow_spec')
        TaskSpec = get_model('task_spec')
        
        for name in tasks:
            spec = TaskSpec(name=name, content=Serial.dump(tasks[name]))
            spec.save()
            
        for name in workflows:
            spec = WorkflowSpec(name=name, content=Serial.dump(workflows[name]))
            spec.save()
