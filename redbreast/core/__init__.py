from const import *
from exception import WFException
from workflow import Workflow
from task import Task

__specs__ = {}

def after_init_apps(sender):
    from uliweb import settings
    if 'SPECS' in settings:
        for alias, spec_klass in settings.SPECS.items():
            register_spec(alias, spec_klass)

def register_spec(alias, spec_klass):
    __specs__[alias] = spec_klass
    
def get_spec(alias):
    return __specs.get(alias, '')
    