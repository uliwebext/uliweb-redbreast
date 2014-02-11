from redbreast.core.utils import *
import pytest

def test_import():
    a = CommonUtils.get_class('redbreast.core.spec.TaskSpec')
    assert str(a) == "<class 'redbreast.core.spec.task.TaskSpec'>"
    
def test_import_not_exist():
    a = CommonUtils.get_class('redbreast.core.spec.NotExistSpec')
    assert str(a) == 'None'
    
def test_import_error():
    with pytest.raises(ImportError):
        a = CommonUtils.get_class('not.exist.module.NotExistSpec')
        
    