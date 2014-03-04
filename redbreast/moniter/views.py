#coding=utf8

from uliweb import expose, functions, settings, decorators
from uliweb.i18n import gettext_lazy as _
import datetime

def __begin__():
    from uliweb import functions
    return functions.require_login()

def task_id(value, obj):
    from uliweb.core.html import Tag
    display = "%04d"%obj.id
    return str(Tag('a', display, href='/redbreast/task/%d' % obj.id))


@expose('/redbreast/')
class MoniterView(object):

    def __init__(self):
        self.wf_model = functions.get_model('workflow')
        self.wftask_model = functions.get_model('workflow_task')

    def __begin__(self):
        if not request.user.is_superuser:
            error('你不是超级用户不能进行这项操作！')

    @expose('')
    @expose('workflows')
    def workflows(self):
        from uliweb.utils.generic import ListView, get_sort_field

        fields = ['id',
            {'name':'spec_name','width':200}, 'desc', 'state',
            'created_user', 'created_date',
            'modified_user', 'modified_date']

        def id(value, obj):
            from uliweb.core.html import Tag
            return str(Tag('a', ("%04d"%obj.id), href='/redbreast/workflow/%d' % obj.id))

        fields_convert_map = {'id': id}
        view = ListView(self.wf_model,
            fields_convert_map=fields_convert_map, fields=fields)

        if 'data' in request.values:
            return json(view.json())
        else:
            result = view.run(head=True, body=False)
            result.update({'table':view})
            return result

    def workflow(self, id):
        from uliweb.utils.generic import DetailView, ListView

        obj = self.wf_model.get(int(id))

        def get_wf_detail():
            fields1 = ['id', 'spec_name',
                'desc', 'state', 'created_user', 'created_date',
                'modified_user', 'modified_date']

            layout1 = [
                    '-- 基本信息 --',
                    ('id', 'state', 'spec_name'),
                    ('desc'),
                    ('created_user', 'created_date'),
                    ('modified_user', 'modified_date'),
                    ]

            view1 = DetailView(self.wf_model, obj=obj, fields=fields1, layout=layout1)
            result1 = view1.run()
            return result1['view']

        fields2 = [ 'id',
            {'name': 'spec_name', 'width':200}, 'desc',
             'state',
            'alias_name', 'created_user', 'created_date', 'modified_user', 'modified_date']

        cond = self.wftask_model.c.workflow == obj.id
        fields_convert_map = {'id': task_id}
        view2 = ListView(self.wftask_model, condition=cond,
            fields_convert_map=fields_convert_map, fields=fields2)

        if 'data' in request.values:
            return json(view2.json())
        else:
            result2 = view2.run(head=True, body=False)
            result2.update({'table':view2, 'detailview': get_wf_detail(), 'workflow': obj})
            return result2

    def tasks(self):
        from uliweb.utils.generic import ListView, get_sort_field

        workflow_id = int(request.GET.get("workflow", -1))

        cond = None
        if workflow_id > 0:
            cond = (self.wftask_model.c.workflow == workflow_id)

        fields = [ 'id',
            {'name': 'spec_name', 'width':200}, 'desc',
             'state',
            {'name': 'workflow', 'width':200},
            'alias_name', 'created_user', 'created_date', 'modified_user', 'modified_date']

        def workflow(value, obj):
            from uliweb.core.html import Tag
            display = obj.workflow.spec_name + ("%04d"%obj.workflow.id)
            tag = Tag('a', display, href='/redbreast/workflow/%d' % obj.workflow.id)
            return str(tag) + ("&nbsp; <a class='btn btn-small btn-primary' href='/redbreast/tasks?workflow=%d'>Filter</a>" % obj.workflow.id)

        fields_convert_map = {'workflow':workflow, 'id': task_id}
        view = ListView(self.wftask_model, condition=cond,
            fields_convert_map=fields_convert_map, fields=fields)

        if 'data' in request.values:
            return json(view.json())
        else:
            result = view.run(head=True, body=False)
            result.update({'table':view})
            return result

    def task(self, id):
        from uliweb.utils.generic import DetailView

        obj = self.wftask_model.get(int(id))

        fields = [ 'id', 'spec_name', 'desc',
             'state', 'workflow',
             'alias_name',
             'created_user', 'created_date',
             'modified_user', 'modified_date',
             {'name': 'inflows', 'verbose_name': '流入'},
             {'name': 'outflows',  'verbose_name': '流出'},
             ]

        layout = [
                '-- 基本信息 --',
                ('id', 'state', 'spec_name'),
                ('desc'),
                ('created_user', 'created_date'),
                ('modified_user', 'modified_date'),
                '-- 流向信息 --',
                ('inflows'),
                ('outflows'),
                ]

        def inflows(value, obj):
            from uliweb.orm import get_model
            WFTrans = get_model('workflow_trans')
            cond = WFTrans.c.to_task == obj.id
            items = []
            for trans in WFTrans.filter(cond):
                if trans.from_task:
                    items.append(u"[%s] -> 由 %s 在 %s 流转" %
                        (trans.from_task.desc, trans.created_user, trans.created_date))

            if len(items)>0:
                return "<br/>".join(items)
            else:
                return ''

        def outflows(value, obj):
            from uliweb.orm import get_model
            WFTrans = get_model('workflow_trans')
            cond = WFTrans.c.from_task == obj.id
            items = []
            for trans in WFTrans.filter(cond):
                if trans.to_task:
                    items.append(u"-> [%s] 由 %s 在 %s 流转" %
                        (trans.to_task.desc, trans.created_user, trans.created_date))

            if len(items)>0:
                return "<br/>".join(items)
            else:
                return ''

        fields_convert_map = {'inflows':inflows, 'outflows': outflows}
        view = DetailView(self.wftask_model, obj=obj,
            fields_convert_map=fields_convert_map,
            fields=fields, layout=layout)
        result = view.run()
        return result


