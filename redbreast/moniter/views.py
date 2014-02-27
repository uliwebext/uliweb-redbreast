#coding=utf8

from uliweb import expose, functions, settings, decorators
from uliweb.i18n import gettext_lazy as _
import datetime

def __begin__():
    from uliweb import functions
    return functions.require_login()

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

        fields = [
            {'name':'spec_name','width':200}, 'desc', 'state', 'created_user', 'created_date', 
        'modified_user', 'modified_date']

        def spec_name(value, obj):
            from uliweb.core.html import Tag
            return str(Tag('a', value + ("%04d"%obj.id), href='/redbreast/workflow/%d' % obj.id))

        fields_convert_map = {'spec_name': spec_name}
        view = ListView(self.wf_model, 
            fields_convert_map=fields_convert_map, fields=fields)

        if 'data' in request.values:
            return json(view.json())
        else:
            result = view.run(head=True, body=False)
            result.update({'table':view})
            return result

    def tasks(self):
        from uliweb.utils.generic import ListView, get_sort_field


        fields = [
            {'name': 'spec_name', 'width':200}, 'desc',
             'state', 
            {'name': 'workflow', 'width':200}, 
            'alias_name', 'created_date', 'modified_user', 'modified_date']   

        def workflow(value, obj):
            from uliweb.core.html import Tag
            display = obj.workflow.spec_name + ("%04d"%obj.workflow.id)
            return str(Tag('a', display, href='/redbreast/workflow/%d' % obj.workflow.id))

        def spec_name(value, obj):
            from uliweb.core.html import Tag
            display = obj.spec_name + ("%04d"%obj.id)
            return str(Tag('a', display, href='/redbreast/task/%d' % obj.id))

        fields_convert_map = {'workflow':workflow, 'spec_name': spec_name}
        view = ListView(self.wftask_model, 
            fields_convert_map=fields_convert_map, fields=fields)

        if 'data' in request.values:
            return json(view.json())
        else:
            result = view.run(head=True, body=False)
            result.update({'table':view})
            return result
