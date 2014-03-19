from redbreast.core.utils import *
import pytest
from uliweb import manage, functions
import os

def test_import():
    a = CommonUtils.get_class('redbreast.core.spec.TaskSpec')
    assert str(a) == "<class 'redbreast.core.spec.task.TaskSpec'>"
    
def test_import_not_exist():
    a = CommonUtils.get_class('redbreast.core.spec.NotExistSpec')
    assert str(a) == 'None'
    
def test_import_error():
    with pytest.raises(ImportError):
        a = CommonUtils.get_class('not.exist.module.NotExistSpec')

class TestUtilInProject(object):
    
    def setup(self):
        locate_dir = os.path.dirname(__file__)
        os.chdir(locate_dir)
        os.chdir('test_project')

        import shutil
        shutil.rmtree('database.db', ignore_errors=True)

        manage.call('uliweb syncdb')
        manage.call('uliweb syncspec')

        from uliweb.manage import make_simple_application
        app = make_simple_application(apps_dir='./apps')
    
    def teardown(self):
        import shutil
        shutil.rmtree('database.db', ignore_errors=True)
    
    def test_import(self):

        maps = {
            'simple_task' :      'redbreast.core.spec.task.SimpleTask',
            'join_task'   :      'redbreast.core.spec.task.JoinTask',
            'choice_task' :      'redbreast.core.spec.task.ChoiceTask',
            'split_task'  :      'redbreast.core.spec.task.SplitTask',
            'multichocie_task' : 'redbreast.core.spec.task.MultiChoiceTask',
            'auto_simple_task' :     'redbreast.core.spec.task.AutoSimpleTask',
            'auto_join_task'   :     'redbreast.core.spec.task.AutoJoinTask',
            'auto_choice_task' :     'redbreast.core.spec.task.AutoChoiceTask',
            'auto_split_task'  :     'redbreast.core.spec.task.AutoSplitTask',
            'auto_multichoice_task' :'redbreast.core.spec.task.AutoMultiChoiceTask',
        }

        for spec in maps:
            a = CommonUtils.get_spec(spec)
            assert str(a) == "<class '%s'>" % maps[spec]

            spec1 = maps[spec].replace("redbreast.core.spec.task.", "")
            b = CommonUtils.get_spec(spec1)
            assert str(b) == "<class '%s'>" % maps[spec]
        
    