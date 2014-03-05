#coding=utf8

from uliweb import expose, functions, settings, decorators
from uliweb.i18n import gettext_lazy as _
from helper import ApproveHelper
from uliweb.contrib.flashmessage import flash
import datetime

def __begin__():
    from uliweb import functions
    return functions.require_login()

def approve_title(value, obj):
    from uliweb.core.html import Tag
    return str(Tag('a', value, href='/approve/view/%d' % obj.id))

def get_deliver_form(from_task, to_tasks):
    from uliweb.form import Form, Button, TextField, HiddenField
    if len(to_tasks) == 1:
        spec_name, desc = to_tasks[0]
        class DeliverForm(Form):
            form_buttons = [Button(value='流转到%s' % desc, _class="btn btn-primary",
                type='button', id='btnDeliver')]

            trans_message = TextField(label='流转意见', html_attrs={'style':'width:80%'})
            from_task_id = HiddenField(label='id',
                html_attrs={'style':'display:none'}, default=from_task.get_unique_id())
    elif len(to_tasks)>1:
        from uliweb.form import SelectField
        choices = to_tasks
        class DeliverForm(Form):
            form_buttons = [Button(value='流转', _class="btn btn-primary",
                type='button', id='btnDeliver')]

            trans_message = TextField(label='流转意见', html_attrs={'style':'width:80%'}, required=True)
            to_tasks = SelectField(label='流转给', choices=choices, required=True)
            from_task_id = HiddenField(label='id',
                html_attrs={'style':'display:none'}, default=from_task.get_unique_id())
    elif len(to_tasks) == 0:
        class DeliverForm(Form):
            form_buttons = [Button(value='办结', _class="btn btn-primary",
                type='button', id='btnDeliver')]

            trans_message = TextField(label='办结意见', html_attrs={'style':'width:80%'}, required=True)
            from_task_id = HiddenField(label='id',
                html_attrs={'style':'display:none'}, default=from_task.get_unique_id())

    return DeliverForm()


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
        from sqlalchemy.sql import or_

        fields_convert_map = {'title': approve_title}
        helper = ApproveHelper()
        spec_names = helper.get_task_spec_names(request.user)
        cond = None
        if len(spec_names) > 0:
            cond = or_(*[self.model.c.task_spec_name == name for name in spec_names])
        print cond

        view = ListView(self.model, condition=cond,
            fields_convert_map=fields_convert_map)

        if 'data' in request.values:
            return json(view.json())
        else:
            result = view.run(head=True, body=False)
            result.update({'table':view})
            return result

    @decorators.check_permission('ApproveWorkflowCreate')
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

    def edit(self, id):
        from uliweb.utils.generic import EditView
        from forms import ApproveEditForm
        from uliweb.form.layout import BootstrapTableLayout

        obj = self.model.get(int(id))
        helper = ApproveHelper()
        helper.bind(obj, get_workflow=True)
        tasks = helper.get_active_tasks()
        if len(tasks) == 1:
            task_id = tasks[0].get_unique_id()
            fields = [{'name': 'trans_message', 'verbose_name':'流转意见'}]

            if helper.has_deliver_permission(tasks[0], request.user):

                task_name = tasks[0].get_name()

                form_cls = ApproveEditForm().get_form(task_name)
                fields = form_cls.fields
                layout = form_cls.layout
                auto_fill_fields = form_cls.auto_fill_fields
                if hasattr(form_cls, 'static_fields'):
                    static_fields = form_cls.static_fields
                else:
                    static_fields = fields[0:-1]

                def pre_save(obj, data):
                    if auto_fill_fields:
                        data[auto_fill_fields[0]] = request.user.id
                        data[auto_fill_fields[1]] = datetime.datetime.now()

                def post_created_form(fcls, model, obj):
                    fcls.layout_class_args = {'table_class':'table width100'}
                    fcls.layout_class = BootstrapTableLayout

                view = EditView(self.model, url_for(self.__class__.view, id=id),
                    fields=fields, static_fields = static_fields,
                    post_created_form=post_created_form,
                    obj=obj, pre_save=pre_save, layout=layout)
                return view.run()
            else:
                flash(u"您没有权限访问编辑填写功能。")
                return redirect(url_for(ApproveView.view, id=id))
        else:
            flash(u"您没有权限访问编辑填写功能。")
            return redirect(url_for(ApproveView.view, id=id))


    def view(self, id):
        from uliweb.utils.generic import DetailView
        from forms import ApproveEditForm

        obj = self.model.get(int(id))

        helper = ApproveHelper()
        helper.bind(obj, get_workflow=True)

        tasks = helper.get_active_tasks()

        if len(tasks) == 1:

            task_id = tasks[0].get_unique_id()
            task_name = tasks[0].get_name()
            form_cls = ApproveEditForm().get_form(task_name)
            auto_fill_fields = form_cls.auto_fill_fields
            fields = form_cls.fields + auto_fill_fields
            layout = form_cls.layout + auto_fill_fields

            view = DetailView(self.model, obj=obj, fields=fields, layout=layout)
            result = view.run()

            data = {
                'detailview': result['view'],
                'obj': result['object'],
                'workflow': helper.get_workflow(),
            }

            fields = [{'name': 'trans_message', 'verbose_name':'流转意见'}]

            if helper.has_deliver_permission(tasks[0], request.user):
                next_tasks = tasks[0].get_next_tasks()
                form = get_deliver_form(tasks[0], next_tasks)

                data.update({
                    'deliverform': form,
                    'show_deliver_form':True,
                    'task_desc': tasks[0].get_desc(),
                    'task_name': tasks[0].get_name()
                })

            else:
                data.update({
                    'show_deliver_form':False,
                    'task_desc': tasks[0].get_desc(),
                    'task_name': tasks[0].get_name()
                })

        else:
            form_cls = ApproveEditForm().get_form("Archiver")
            auto_fill_fields = form_cls.auto_fill_fields
            fields = form_cls.fields + auto_fill_fields
            layout = form_cls.layout + auto_fill_fields

            view = DetailView(self.model, obj=obj, fields=fields, layout=layout)
            result = view.run()

            data = {
                'detailview': result['view'],
                'obj': result['object'],
                'workflow': helper.get_workflow(),
            }
            data.update({
                'show_deliver_form': False,
                'task_desc': None
            })

        return data

    def deliver(self, id):
        obj = self.model.get(int(id))
        helper = ApproveHelper()
        helper.bind(obj, get_workflow=True)
        tasks = helper.get_active_tasks()

        if len(tasks) == 1:
            task_id = tasks[0].get_unique_id()
            next_tasks = tasks[0].get_next_tasks()

            from_task_id = request.POST.get('from_task_id')
            if from_task_id != task_id:
                return json({'success': False, 'message': '无效的标识，请求的活动可能已经被他人流转。'})

            trans_message = request.POST.get('trans_message', '')
            if len(next_tasks)>1:
                to_tasks = request.POST.get('to_tasks', None)
                if not to_tasks:
                    return json({'success': False, 'message': '无效的请求，您没有指定需要流转的流向。'})

                helper.deliver(trans_message, next_tasks=[to_tasks])
            else:
                helper.deliver(trans_message)


            return json({'success': True})
        else:
            return json({'success': False, 'message': '无效的请求，请求的活动可能已经被他人流转。'})




