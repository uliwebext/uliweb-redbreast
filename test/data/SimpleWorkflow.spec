task S1:
end

task S2:
end


process SimpleWorkflow:
    flows:
        S1 -> S2
    end
end