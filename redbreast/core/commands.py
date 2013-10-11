import os
from optparse import make_option
from uliweb.core.commands import Command, get_input, get_answer
from uliweb.core.template import template_file

class ClearSpecCommand(Command):
    name = 'clear_spec'
    help = 'delete all workflow specs from database.'
    check_apps = True
    
    
    def handle(self, options, global_options, *args):
        from uliweb.orm import get_model
        
        message = """This command will delete all workflow specs, are you sure to do?"""
        get_answer(message)
        
        self.get_application(global_options)
        
        WorkflowSpec = get_model('workflow_spec')
        TaskSpec = get_model('task_spec')
        
        print "Deleting Workflow_Spec ..."
        WorkflowSpec.remove()
        print "Deleting Task_Spec  ..."
        TaskSpec.remove()
    
    
class SyncSpecCommand(Command):
    name = 'sync_spec'
    
    def handle(self, options, global_options, *args):
        from uliweb.core.SimpleFrame import get_app_dir

        apps_list = self.get_apps(global_options)
        for p in apps_list:
            spec_dir =os.path.join(get_app_dir(p), 'workflow_specs')
            if os.path.isdir(spec_dir):
                for f in os.listdir(spec_dir):
                    if f.endswith('.spec'):
                        file = os.path.join(spec_dir, f)
                        print "Parsing file %s ...." % file
                        #TODO: 
                        #  parse this file and 
                        #  save workflow spec to database

class ReloadSpecCommand(Command):
    name = 'reload_spec'
    
    def handle(self, options, global_options, *args):
        from uliweb.orm import get_model
        from uliweb.core.SimpleFrame import get_app_dir
        
        from redbreast.core.spec import parse, parseFile
        
        message = """This command will delete all workflow specs, are you sure to do?"""
        get_answer(message)

        self.get_application(global_options)

        WorkflowSpec = get_model('workflow_spec')
        TaskSpec = get_model('task_spec')

        print "Deleting Workflow_Spec ..."
        WorkflowSpec.remove()
        print "Deleting Task_Spec  ..."
        TaskSpec.remove()
        print ""
        
        apps_list = self.get_apps(global_options)
        for p in apps_list:
            spec_dir =os.path.join(get_app_dir(p), 'workflow_specs')
            if os.path.isdir(spec_dir):
                for f in os.listdir(spec_dir):
                    if f.endswith('.spec'):
                        file = os.path.join(spec_dir, f)
                        print "Parsing file %s ...." % file
                        tasks, processes = parseFile(file)
                        print tasks
                        print processes
                        
                        #TODO: 
                        #  parse this file and 
                        #  save workflow spec to database
        
