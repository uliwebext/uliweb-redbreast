#coding=utf8

from uliweb import expose, functions, settings, decorators
from uliweb.i18n import gettext_lazy as _
from helper import ApproveHelper
import datetime

def __begin__():
    from uliweb import functions
    return functions.require_login()

def approve_title(value, obj):
    from uliweb.core.html import Tag
    return str(Tag('a', value, href='/approve/view/%d' % obj.id))


@expose('/approve/')
class ApproveView(object):

    def __init__(self):
        self.model = functions.get_model('approve')

    def list(self):
    	from uliweb.utils.generic import ListView, get_sort_field
        fields_convert_map = {'title': approve_title}
        view = ListView(self.model, fields_convert_map=fields_convert_map)

        if 'data' in request.values:
            return json(view.json())
        else:
            result = view.run(head=True, body=False)
            result.update({'table':view})
            return result

    def mylist(self):
        from uliweb.utils.generic import ListView, get_sort_field
        fields_convert_map = {'title': approve_title}
        cond = (self.model.c.submitter == request.user.id)
        view = ListView(self.model, condition=cond,
            fields_convert_map=fields_convert_map)

        if 'data' in request.values:
            return json(view.json())
        else:
            result = view.run(head=True, body=False)
            result.update({'table':view})
            return result

    def todolist(self):
        from uliweb.utils.generic import ListView, get_sort_field
        fields_convert_map = {'title': approve_title}
        view = ListView(self.model, fields_convert_map=fields_convert_map)

        if 'data' in request.values:
            return json(view.json())
        else:
            result = view.run(head=True, body=False)
            result.update({'table':view})
            return result

    @decorators.check_permission('ApproveCreate')
    def add(self):
        from uliweb.utils.generic import AddView


        helper = ApproveHelper()

        def pre_save(data):
            data['submitter'] = request.user.id
            data['submitter_date'] = datetime.datetime.now()

        def post_save(obj, data):
        	helper.bind(obj)
        	helper.create_workflow()

        view = AddView(self.model, url_for(self.__class__.list),
        	 pre_save=pre_save, post_save=post_save)

        result = view.run()
        return result

    def view(self, id):
        from uliweb.utils.generic import DetailView

        obj = self.model.get(int(id))

        fields = ('title','content','submitter','submitter_date')
        layout = [
                '-- 评审单基本信息 --',
                ('title'),
                ('content'),
                ('submitter', 'submitter_date'),
                ]

        view = DetailView(self.model, obj=obj, fields=fields, layout=layout)
        result = view.run()

        helper = ApproveHelper()
        helper.bind(obj, get_workflow=True)
        state = helper.get_workflow_state()


        data = {'detailview': result['view'], 'state': state}

        return data

