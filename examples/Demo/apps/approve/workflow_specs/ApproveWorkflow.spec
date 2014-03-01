# 创建审批流程
task CreateApproveTask:
"""创建审批"""
    class : simple_task
end

# 小组内部预审
task GroupApproveTask:
"""小组预审"""
    class : simple_task
end

# 部门管理员审批
task DepartApproveTask:
"""部门管理员审批"""
    #多选节点
    class : choice_task
end

# 分管领导审批
task ManagerApproveTask:
"""分管领导审批"""
    class : simple_task
end

# 大领导直接审批
task BossApproveTask:
"""中心领导审批"""
    class : simple_task
end

# 结果审核
task CheckerTask:
"""审核"""
    class : simple_task
end

# 归档
task ArchiverTask:
"""归档"""
    class : simple_task
end

process ApproveWorkflow:
    '''
    审批流程
    '''
    tasks:
        # 别名定义
        CreateApproveTask   as Create
        GroupApproveTask    as Group
        DepartApproveTask   as Depart
        ManagerApproveTask  as Manager
        BossApproveTask     as Boss
        CheckerTask         as Checker
        ArchiverTask        as Archiver
    end

    # 流向定义
    flows:
        # 流向可以分成多行
        Create->Group->Depart
            Depart->Manager->Checker
            Depart->Boss->Checker
        Checker->Archiver
    end

end
