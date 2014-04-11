#!/usr/bin/python
# -*- coding: utf-8 -*-
import gevent, pymysql
import gevent.monkey
gevent.monkey.patch_all()
#pymysql.install_as_MySQLdb()

_path = None

def setup():
    import os
    global _path
    _path = os.getcwd()
    locate_dir = os.path.dirname(__file__)
    os.chdir(os.path.abspath(locate_dir))
    os.chdir('test_project')

    from uliweb.manage import make_simple_application
    app = make_simple_application(apps_dir='./apps')         

def teardown():
    import os
    global _path
    #self.remove_database()
    os.chdir(_path)    

def test2():
    from uliweb.orm import get_model
    TaskDB = get_model('workflow_task')  
    query = TaskDB.filter(None).limit(5)
    ids = [task_obj.id for task_obj in query]

def test(i):
    from uliweb.orm import get_model
    from uliweb.orm import Begin, Commit, Rollback

    try:
        Begin()
        TaskDB = get_model('workflow_task')  
        cond = None
        query = TaskDB.filter(cond).limit(10)
        ids = [task_obj.id for task_obj in query]

        Commit(close=True)
    except:
        Rollback()    
        raise

    from uliweb.orm import print_pool_status

    print_pool_status()
    from random import randint
    if randint(1,2) == 1:
        test2()
    else:
        import gevent
        gevent.sleep(0.5)
    print i
    return

def goodquery(sql, i):
    db = pymysql.connect(host = 'localhost', passwd = '111', us er = 'root', db= 'redbreasttestdb')
    cursor = db.cursor()
    data = cursor.execute(sql)
    cursor.close()
    db.close()
    return cursor

def main():
    jobs = []
    for i in range(0, 10):
        jobs.append(gevent.spawn(test, i))

    gevent.joinall(jobs)

def main1():
    jobs = []
    for i in range(0, 10):
        test(i)


if __name__ == '__main__':
    setup()
    import time
    begin = time.clock()
    print "-----------1"
    main1()
    print "-----------2 %s" % (time.clock()-begin)

    begin = time.clock()
    print "-----------1"
    main()
    print "-----------2 %s" % (time.clock()-begin)
    teardown()

    #import timeit
    #print(timeit.timeit("main()", setup="from __main__ import main", number=1))                
