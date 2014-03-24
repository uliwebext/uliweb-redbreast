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
    
def loadspec(apps_list, global_options):
    from uliweb.core.SimpleFrame import get_app_dir
    from uliweb import settings
    from redbreast.core.spec import parse, parseFile
    
    SPEC_DIR = settings.REDBREAST.SPEC_DIR
    SPEC_SUFFIX = settings.REDBREAST.SPEC_SUFFIX
    
    all_tasks = {}
    all_workflows = {}
    
    for p in apps_list:
        spec_dir =os.path.join(get_app_dir(p), SPEC_DIR)
        if os.path.isdir(spec_dir):
            for f in os.listdir(spec_dir):
                if f.endswith(SPEC_SUFFIX):
                    file = os.path.join(spec_dir, f)
                    print "\n* Parsing file %s ...." % file
                    
                    try:
                        tasks, processes = parseFile(file)
                        print tasks
                        print processes
                    except Exception, e:
                        print "[ERROR] ParseError, %s" % e
                        tasks, processes = {}, {}
                        
                    if global_options.verbose:
                        print "   tasks, %s, %s" % (len(tasks), [t for t in tasks])
                        print "   workflow, %s, %s" % (len(processes), [t for t in processes])
                    
                    for name in tasks:
                        if name in all_tasks:
                            print "[WARNING] duplicate definition of Task %s" % (name)
                            print "    will be overwriten by lastest one in %s" % file
                        all_tasks[name] = (tasks[name], file)
                            
                    for name in processes:
                        if name in all_workflows:
                            print "[WARNING] duplicate definition of Workflow %s" % (name)
                            print "    will be overwriten by lastest one in %s" % file
                        all_workflows[name] = (processes[name], file)
                    
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
    help = 'update new added workflow specs into database.'
    
    def handle(self, options, global_options, *args):
        
        apps_list = self.get_apps(global_options)
        self.get_application(global_options)
        
        tasks, workflows = loadspec(apps_list, global_options)
        
        print "\n"
        
        from uliweb.orm import get_model
        from uliweb.utils.common import Serial
        WorkflowSpec = get_model('workflow_spec')
        TaskSpec = get_model('task_spec')
        
        for name in tasks:
            
            find = TaskSpec.get(TaskSpec.c.name==name)
            task, file = tasks[name]
            if not find:
                spec = TaskSpec(name=name, content=Serial.dump(task), source=file)
                spec.save()
            else:
                if global_options.verbose:
                    print "[WARNING] Task Spec %s is existed, will be udated." % name
                    
                find.update(content=Serial.dump(task), source=file)
                find.save()
        
        for name in workflows:
            
            find = WorkflowSpec.get(WorkflowSpec.c.name==name)
            workflow, file = workflows[name]
            if not find:
                spec = WorkflowSpec(name=name, content=Serial.dump(workflow), source=file)
                spec.save()
            else:
                if global_options.verbose:
                    print "[WARNING] Workflow Spec %s is existed, will be updated." % name
                
                find.update(content=Serial.dump(workflow), source=file)
                find.save()
        
        
        
class ShowSpecCommand(Command):
    name = 'showspec'
    help = 'list all workflow specs in database.'
    option_list = (
        make_option('-d', '--detail', dest='detail', action='store_true', default=False,
            help='Show the detail of every specs.'),
    )
    has_options = True
    
    def handle(self, options, global_options, *args):
        from uliweb.orm import get_model
        from uliweb.utils.common import Serial
        import pprint
        
        self.get_application(global_options)
        WorkflowSpec = get_model('workflow_spec')
        TaskSpec = get_model('task_spec')
        
        print "TaskSpec : %s" % (TaskSpec.all().count())
        for task in TaskSpec.all():
            print " * %s" % task.name
            if global_options.verbose:
                print "   - modified_date: %s" % task.modified_date
                print "   - source: %s" % task.source
            if options.detail:
                pprint.pprint(Serial.load(task.content))
        
        print "\nWorkflowSpec : %s" % (WorkflowSpec.all().count())
        for wf in WorkflowSpec.all():
            print " * %s" % wf.name
            if global_options.verbose:
                print "   - modified_date: %s" % wf.modified_date
                print "   - source: %s" % wf.source
            if options.detail:
                pprint.pprint(Serial.load(wf.content))

class ReloadSpecCommand(Command):
    name = 'reloadspec'
    help = 'reparse all workflow specs from config file and store them into database.'
    option_list = (
        make_option('-t', '--test', dest='test', action='store_true', default=False,
            help='Parse config file but not store them.'),
        make_option('-y', '--yes', dest='skip_warning', action='store_true', default=False,
            help='Skip warning information, and always execute next step.')
            
    )
    has_options = True
    
    def handle(self, options, global_options, *args):
        from uliweb.orm import get_model
        from uliweb.core.SimpleFrame import get_app_dir
        
        if not options.test:
            if not options.skip_warning:
                message = """This command will delete all workflow specs, are you sure to do?"""
                get_answer(message)

        self.get_application(global_options)
        
        if not options.test:
            clear()
            print ""
        
        apps_list = self.get_apps(global_options)
        tasks, workflows = loadspec(apps_list, global_options)
        
        from uliweb.orm import get_model
        from uliweb.utils.common import Serial
        WorkflowSpec = get_model('workflow_spec')
        TaskSpec = get_model('task_spec')
        
        if not options.test:
            for name in tasks:
                task, file = tasks[name]
                spec = TaskSpec(name=name, content=Serial.dump(task), source=file)
                spec.save()
            
            for name in workflows:
                workflow, file = workflows[name]
                spec = WorkflowSpec(name=name, content=Serial.dump(workflow), source=file)
                spec.save()
