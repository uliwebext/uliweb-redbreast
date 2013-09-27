class WFResult(object):
    def __init__(self, type="none", msg=""):
        super(WFResult, self).__init__()
        self.type = type
        self.msg = None
        
    def __eq__(self, result):
        if result == True:
            result = YES
        if result == False:
            result = NO
        return self.type == result.type
    
    def __call__(self, msg=None):
        ret = WFResult()
        ret.type = self.type
        ret.msg = msg
        return ret
    
    def __str__(self):
        if self.msg:
            return "%s - %s" % (self.type, self.msg)
        return self.type
    
class WFResultTask(WFResult):
    
    def __call__(self, msg=None, *args):
        ret = WFResultTask()
        ret.type = self.type
        ret.list = set(args)
        ret.msg = msg
        return ret   
    
    def union(self, list):
        ret = WFResultTask(type="TASK")
        ret.list = set()
        for task in list:
            if isinstance(task, str):
                ret.list.add(task)
            else:
                ret.list.union(task.list)
        
        return ret
    
    def __contains__(self, task_name):
        return task_name in self.list

YES = WFResult(type="YES")
NO = WFResult(type="NO")
DONE = WFResult(type="DONE")
DOING = WFResult(type="DOING")
TASK = WFResultTask(type="TASK")

def inject_const_scope(scope):
    scope['YES']   = YES
    scope['NO' ]   = NO
    scope['DONE']  = DONE
    scope['DOING'] = DOING
    return scope
