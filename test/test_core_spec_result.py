from redbreast.core.spec import *


class TestCoreSpecResult(object):
	
	def test_yes_no(self):
		assert YES == WFResult(type="YES")
		assert YES != NO
		assert YES != WFResult(type="NO")
		assert YES == True
		assert NO == False
		assert YES == YES(msg="with a message")
		assert NO == NO(msg="error message")

	def test_task_result(self):
		task1 = "TASK1"
		task2 = "TASK2"
		task3 = "TASK3"

		ret_tasks = TASK.union([task1,task2]).union(task3)

		print ret_tasks.list

		assert (task1 in ret_tasks) == True
		assert (task2 in ret_tasks) == True
		assert (task3 in ret_tasks) == True

		ret_tasks = TASK(task1,task2,task3)

		print ret_tasks.list

		assert (task1 in ret_tasks) == True
		assert (task2 in ret_tasks) == True
		assert (task3 in ret_tasks) == True

		ret_tasks = TASK.union(task1).union(task2).union(task3)

		print ret_tasks.list

		assert (task1 in ret_tasks) == True
		assert (task2 in ret_tasks) == True
		assert (task3 in ret_tasks) == True

		ret_tasks = TASK.union([task1]).union([task2]).union(TASK(task3))

		print ret_tasks.list

		assert (task1 in ret_tasks) == True
		assert (task2 in ret_tasks) == True
		assert (task3 in ret_tasks) == True
