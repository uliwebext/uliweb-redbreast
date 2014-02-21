# 创建审批流程
task CreateApproveTask:
    class : simple_task
end

# 小组内部预审
task GroupApproveTask:
    class : simple_task
end

# 部门管理员审批
task DepartApproveTask:
    #多选节点
    class : choice_task
end

# 分管领导审批
task ManagerApproveTask:
    class : simple_task
end

# 大领导直接审批
task BossApproveTask:
    class : simple_task
end

# 结果审核
task CheckerTask:
    class : simple_task
end

# 归档
task ArchiverTask:
    class : simple_task
end

process ApproveWorkflow:
    '''
    Approve Workflow
    '''
    tasks:
        # 别名定义
        CreateApproveTask   as Create
        GroupApproveTask    as Group
        DepartApproveTask   as Depart
        ManagerApproveTask  as Manger
        BossApproveTask     as Boss
        CheckerTask         as Checker
        ArchiverTask        as Archiver
    end
    
    # 流向定义
    flows:
        # 流向可以分成多行
        Create->Group->Depart
            Depart->Manger->Checker
            Depart->Manger->Checker
        Checker->Archiver
    end
    
end
