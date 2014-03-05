
# Readme for Demo project


# Database initalization
 * uliweb reset
 * uliweb syncspec
 * uliweb dbinit

# Snippets

* create new workflow

>   workflow = Workflow.create("ApproveWorkflow", operator=user)
>   workflow.start()
>   workflow.get_id() # ID in database

* restore workflow from record in database

>   Workflow.load(datebase_id, operator=user)

* deliver to next_task

>   tasks = workflow.get_active_tasks()
>   next_tasks = task.get_next_tasks()

>   workflow.deliver(task.uuid, message=message, 
>       next_tasks=next_tasks, async=False)
or 
>   task.deliver(message=message, next_tasks=next_tasks, async=async)


