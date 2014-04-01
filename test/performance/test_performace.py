from uliweb import manage, functions
import os

class TestPerformace(object):

    def remove_database(self):
        import os
        if os.path.exists('database.db'):
            os.remove('database.db')

    def create_database(self):
        self.remove_database()
        manage.call('uliweb syncdb')
        manage.call('uliweb syncspec')

    def setup(self):

        import os
        locate_dir = os.path.dirname(__file__)
        os.chdir(locate_dir)
        os.chdir('test_project')
        self.create_database()

        from uliweb.manage import make_simple_application
        app = make_simple_application(apps_dir='./apps')        
        
    def teardown(self):
        self.remove_database()

    def deliver(self, workflow, uuid, message, next_tasks=None):
        async = False
        workflow.deliver(uuid, message=message, next_tasks=next_tasks, async=async)

    def test(self):
        from uliweb import functions

        Workflow = functions.get_workflow()
        WORKFLOW_SPEC_NAME = "TestWorkflow1"
        #create some workflows
        n = 5
        for i in range(0, n):
            workflow = Workflow.create(WORKFLOW_SPEC_NAME)
            workflow.ref_unique_id = "wf%s" % (i+1)
            workflow.start()

            tasks = workflow.get_active_tasks()
            print "Create workflow %s" % workflow.ref_unique_id

        TaskDB = functions.get_model('workflow_task')
        while True:
            cond = TaskDB.c.state == '1' # ACTIVE
            query = TaskDB.filter(cond)
            print "loop -------------------------------------"
            ids = [task_obj.id for task_obj in query]

            if ids:
                print "ids: %s" % ids
                for aid in ids:
                    task_obj = TaskDB.get(aid)
                    #print "task_obj.id -- %d" % task_obj.id
                    wf_id = task_obj._workflow_
                    workflow = Workflow.load(wf_id)
                    #print "deliver workflow %s" % workflow.ref_unique_id

                    tasks = workflow.get_active_tasks()

                    if len(tasks) == 1:

                        task_id = tasks[0].get_unique_id()
                        task_name = tasks[0].get_name()
                        next_tasks = tasks[0].get_next_tasks()

                        # print "tasks - %s" %task_name

                        if len(next_tasks)>1:
                            to_tasks = next_tasks[0][0]
                            workflow.deliver(task_id, message="Auto", next_tasks=[to_tasks], async=False)
                        else:
                            workflow.deliver(task_id, message="Auto", async=False)
            else:
                break

        print "Done"

if __name__ == '__main__':
    from uliweb.orm import begin_sql_monitor, close_sql_monitor
    test = TestPerformace()
    
    test.setup()
    monitor = begin_sql_monitor(key_length=120, record_details=False)
    test.test()
    monitor.print_()
    close_sql_monitor(monitor)
    #test.teardown()