from redbreast.core.spec.parser import parse, parseFile
from os.path import dirname, join

class TestSpecParser(object):
    
    def test_tasks(self):
        text = """
            task task1:
                '''
                task1 desc
                '''
                class : a.b.c
                
            end
            
            task task2(task1):
                '''
                task2 desc
                '''
            end
            
            task task3(task1):
                class : c.d.e
            end
        """
        tasks, procs = parse(text)
        
        assert len(tasks) == 3
        assert tasks.get('task1') != None
        assert tasks.get('task2') != None
        assert tasks.get('task1').get('class') == "a.b.c"
        assert tasks.get('task2').get('class') == "a.b.c"
        assert tasks.get('task3').get('class') == "c.d.e"
        
        assert tasks.get('task1').get('desc') == "task1 desc"
        assert tasks.get('task2').get('desc') == "task2 desc"
        assert tasks.get('task3').get('desc') == "task1 desc"
        
    def test_workflow(self):
        config_file = join(dirname(__file__), "data/TestWorkflow.config")
        tasks, procs = parseFile(config_file)
        assert len(procs) == 1
        
        for name in procs:
            print procs[name]
            assert len(procs[name].get('tasks')) == 8
            assert len(procs[name].get('flows')) == 8
            shouldbe = [('A', 'B'), ('B', 'C'), ('C', 'G'), ('G', 'H'), ('A', 'D'), ('D', 'E'), ('E', 'F'), ('F', 'G')]
            assert procs[name].get('flows') == shouldbe
            
