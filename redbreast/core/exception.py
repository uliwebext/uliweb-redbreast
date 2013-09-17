

class WFException(Exception):
    def __init__(self, error, sender=None):
        if sender:
            Exception.__init__(self, '%s: %s' % (sender.name, error))
            # Points to the Task that generated the exception.
            self.sender = sender 
        else:
            Exception.__init__(self, '%s' % (error))

class WFKeyError(WFException): pass
    