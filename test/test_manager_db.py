from redbreast.core.spec import CoreWFManager, WFManager
from redbreast.core.spec import *
from uliweb import manage, functions
import os

class TestCoreWFManager(object):
    
    def setup(self):
        manage.call('uliweb makeproject -f TestProject')
        os.chdir('TestProject')
        self.path = os.getcwd()
    
    def teardown(self):
        import shutil
        os.chdir('..')
        if os.path.exists('TestProject'):
            shutil.rmtree('TestProject', ignore_errors=True)
    
    def test_manager_in_project(self):
        
        assert functions.get_model('workflowspec')
