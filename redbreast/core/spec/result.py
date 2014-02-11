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

    def __init__(self, type="TASK", msg=""):
        super(WFResultTask, self).__init__(type, msg)
        self.list = set()
    
    def __call__(self, *args):
        ret = WFResultTask()
        ret.type = self.type
        ret.list = set(args)
        return ret   
    
    def union(self, result_list):
        ret = WFResultTask(type="TASK")
        ret.list = self.list.copy()
        if isinstance(result_list, str):
            ret.list.add(result_list)
        if isinstance(result_list, WFResultTask):
            ret.list = ret.list.union(result_list.list)
        if isinstance(result_list, list) or isinstance(result_list, tuple):
            for task in result_list:
                if isinstance(task, str):
                    ret.list.add(task)
                if isinstance(task, WFResultTask):
                    ret.list = ret.list.union(task.list)
        
        return ret
    
    def __contains__(self, task_name):
        return task_name in self.list

    def print_list(self):
        for task in self.list:
            print "%s" % task

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
