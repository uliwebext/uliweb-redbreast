import logging

LOG = logging.getLogger("redbreast")

#-----------------------------------------------
# Exception, where prefix WF is a shortcut for Workflow

class WFException(Exception):
    def __init__(self, error, sender=None):
        if sender and hasattr(sender, 'name'):
            Exception.__init__(self, '%s: %s' % (sender.name, error))
            # Points to the Task that generated the exception.
            self.sender = sender
        else:
            Exception.__init__(self, '%s' % (error))

class WFEventException(WFException): pass
class WFKeyError(WFException): pass

#-----------------------------------------------
# TaskSpecAlias

__specs__ = {}
__instance_klasses__ = {}

def after_init_apps(sender):
    from uliweb import settings
    if 'SPECS' in settings:
        for alias, spec_klass in settings.SPECS.items():
            register_spec(alias, spec_klass)

    if 'INSTANCES' in settings:
        for name, instance_klass in settings.INSTANCES.items():
            register_instance_klass(name, instance_klass)


def register_spec(alias, spec_klass):
    __specs__[alias] = spec_klass

def get_spec(alias):
    return __specs__.get(alias, '')

def register_instance_klass(name, klass):
    __instance_klasses__[name.upper()] = klass

def get_instance_klass(name):

    klass = __instance_klasses__.get(name.upper())

    mod, name = klass.rsplit(".", 1)
    m = __import__(mod, fromlist=['*'])
    instance = getattr(m, name)
    return instance

from workflow import Workflow
from task import Task

def get_workflow(name='workflow'):
    return get_instance_klass(name)

def get_task(name='task'):
    return get_instance_klass(name)

