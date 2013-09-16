

class WFException(Exception):
    def __init__(self, sender, error):
        Exception.__init__(self, '%s: %s' % (sender.name, error))
        self.sender = sender # Points to the Task that generated the exception.
