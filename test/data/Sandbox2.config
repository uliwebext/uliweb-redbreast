task TaskA:
    class : redbreast.core.spec.SimpleTask
end

task TaskB(TaskA):
end

task TaskC(TaskA):
end

task TaskD(TaskA):
end

task TaskE(TaskA):
end

task TaskF(TaskA):
    class : redbreast.core.spec.JoinTask
end

task TaskG(TaskA):
end

task TaskH(TaskA):
    class : redbreast.core.spec.JoinTask
end

task TaskI(TaskA):
end

process TestWorkflow:
    '''
    desc This is a small workflow definination for testing.
    '''
    key : value
    
    tasks:
        TaskA as A
        TaskB as B
        TaskC as C
        TaskD as D
        TaskE as E
        TaskF as F
        TaskG as G
        TaskH as H
        TaskI as I
    end
    
    flows:
        A->B->C->D->F
        C->E->F->H
        B->G->H
    end
    
end
