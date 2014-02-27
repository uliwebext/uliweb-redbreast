#coding=utf8

from uliweb import expose, functions, settings, decorators
from uliweb.i18n import gettext_lazy as _
import datetime

def __begin__():
    from uliweb import functions
    return functions.require_login()

@expose('/approve/')
class ApproveView(object):

    def __init__(self):
        self.model = functions.get_model('approve')

    def list(self):
    	from uliweb.utils.generic import ListView, get_sort_field
        view = ListView(self.model)

        if 'data' in request.values:
            return json(view.json())
        else:
            result = view.run(head=True, body=False)
            result.update({'table':view})
            return result

    @decorators.check_role('wf_create')
    def add(self):
        from uliweb.utils.generic import AddView
        from helper import ApproveHelper

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
        pass


