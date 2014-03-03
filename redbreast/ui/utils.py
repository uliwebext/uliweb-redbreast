from layout import *


TRANS_TEMPLATE = ""

class WorkflowUIUtils(object):

    @staticmethod
    def print_workflow_trans(workflow, layout_class=WFTransListLayout):
        from uliweb.orm import get_model
        WFTrans = get_model('workflow_trans')
        if hasattr(workflow, 'id'):
            cond = WFTrans.c.workflow == workflow.id
        else:
            cond = WFTrans.c.workflow == workflow.get_id()

        trans = WFTrans.filter(cond).order_by(WFTrans.c.created_date.asc())
        layout = layout_class(trans)

        return layout.html()



