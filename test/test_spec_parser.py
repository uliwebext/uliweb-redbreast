from redbreast.core.spec.parser import parse, parseFile

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
        
        
        