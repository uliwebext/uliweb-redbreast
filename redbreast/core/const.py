class WFConst(object):
    
    #Task_Events
    EVENT_TASK_ENTER     = "event_task_enter"
    EVENT_TASK_READY     = "event_task_ready"
    EVENT_TASK_EXECUTED  = "event_task_executed"
    EVENT_TASK_EXECUTING = "event_task_executing"
    EVENT_TASK_COMPLETED = "event_task_completed"
    
    #Workflow_Events
    EVENT_WF_CREATED   = "event_workflow_created"
    EVENT_WF_PAUSED    = "event_workflow_paused"
    EVENT_WF_FINISHED  = "event_workflow_finished"
    
    EVENT_WF_ADDTASK   = "event_workflow_addtask"
    
    #TaskProxy FlowType
    FLOW_START   =  "flowStart"    #StartTask, only have output tasks
    FLOW_END     =  "flowEnd"      #EndTask, only have input tasks
    FLOW_NORMAL  =  "flowNormal"   #NormalTask, both have input and output tasks 
    FLOW_SINGLE  =  "flowSingle"   #SingleTask, no inut and no output


