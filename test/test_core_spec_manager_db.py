from redbreast.core.spec import CoreWFManager, WFManager
from redbreast.core.spec import *
from uliweb import manage, functions
import os

class TestCoreWFManagerDB(object):
    
    def reset_database(self):
        import os
        os.remove('database.db')
        manage.call('uliweb syncdb')
    
    def setup(self):
        
        locate_dir = os.path.dirname(__file__)
        os.chdir(locate_dir)
        os.chdir('test_project')
        self.reset_database()
        manage.call('uliweb syncspec')
        self.path = os.getcwd()

        from uliweb.manage import make_simple_application
        app = make_simple_application(apps_dir='./apps')
        
        print app
        from uliweb import settings
        print settings.SPECS
        from redbreast.core.spec import WFDatabaseStorage
        
        CoreWFManager.reset()
        #storage = WFDatabaseStorage()
        #CoreWFManager.set_storage(storage)
    
    def teardown(self):
        import shutil
        shutil.rmtree('database.db', ignore_errors=True)
    
    def test_manager_in_project(self):
        assert functions.get_model('workflow_spec')
        assert functions.get_model('task_spec')

    def test_storage_in_project(self):
        output_text = """A (SimpleTask-Start)
   --> B (SimpleTask)
   |      --> C (SimpleTask)
   |             --> G (JoinTask)
   |                    --> H (SimpleTask-End)
   --> D (SimpleTask)
          --> E (SimpleTask)
                 --> F (SimpleTask)
                        --> [shown earlier] G (JoinTask)
"""
        workflow_spec = CoreWFManager.get_workflow_spec('TestWorkflow')
        workflow_spec.dump(verbose=False)
        assert workflow_spec.get_dump(verbose=False) == output_text
        
        