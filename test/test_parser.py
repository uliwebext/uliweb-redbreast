#coding=utf8
import sys
sys.path.insert(0, '..')
from redbreast.core.spec.parser import WorkflowGrammar, WorkflowVisitor

if __name__ == '__main__':
    text = """
task task1:
    '''
    desc abc def;
    '''
    class : a.b.c
end

task task2(task1):
end

task task3(task1):
end

process workflow:
    '''
    desc text abc def
    '''
    key : value
    
    tasks:
        task1 as A, B
    end
    
    flows:
        A->B->task3
        A->task1->task2->task3
    end
    
    code A.ready:
        if data.get("is_superuser") == True:
        	return Task('B')
        else:
        	return Task('task1')
    end
    
    code B.ready:
        return Task('task1')
    end
end

process workflow1:
    '''
    desc text abc def
    '''
    key : value
end
"""

    def parse(text):
        from pprint import pprint
        g = WorkflowGrammar()
        resultSoFar = []
        result, rest = g.parse(text, resultSoFar=resultSoFar, skipWS=False
#            ,root=g['process_code']
            )
        v = WorkflowVisitor(g)
        print result[0].render()
        #print rest
        v.visit(result, True)
        pprint(v.tasks)
        pprint(v.processes)
        
        for pk, pv in v.processes.items():
            for k, v in pv['flows'].items():
                print "key:%s" % k
                print "value:%s" % v
            for k, code in pv['codes'].items():
                print '--KEY: %s---------' % k
                print code
                print '---------------'

    x = parse(text)
    