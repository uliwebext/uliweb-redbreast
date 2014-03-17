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

def after_init_apps(sender):
    from uliweb import settings
    if 'SPECS' in settings:
        for alias, spec_klass in settings.SPECS.items():
            register_spec(alias, spec_klass)

def register_spec(alias, spec_klass):
    __specs__[alias] = spec_klass

def get_spec(alias):
    return __specs__.get(alias, '')

from workflow import Workflow
from task import Task


