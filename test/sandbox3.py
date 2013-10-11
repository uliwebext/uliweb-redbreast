class WFResult(object):
    def __init__(self, type="none", msg=""):
        super(WFResult, self).__init__()
        self.type = type
        self.msg = None
        
    def __eq__(self, result):
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

YES = WFResult(type="YES")
NO = WFResult(type="NO")
DONE = WFResult(type="DONE")
DOING = WFResult(type="DOING")


a = YES()
b = NO()
c = NO(msg="aaa")

print a
print b
print c
print "a-", id(a), "-", a
print "b-", id(b), "-", b
print "c-", id(c), "-", c

print "a,b=", a==b
print "a,YES=", a==YES
print "NO,b=", NO==b
print "b,c=", b==c
print "NO,c=", NO==c
