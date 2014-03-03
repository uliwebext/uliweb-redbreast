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
        fields_convert_map = {'title': approve_title}
        view = ListView(self.model, fields_convert_map=fields_convert_map)

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

        obj = self.model.get(int(id))
        helper = ApproveHelper()
        helper.bind(obj, get_workflow=True)
        tasks = helper.get_active_tasks()
        if len(tasks) == 1:
            task_id = tasks[0].get_unique_id()
            fields = [{'name': 'trans_message', 'verbose_name':'流转意见'}]

            if helper.has_deliver_permission(tasks[0], request.user):

                task_name = tasks[0].get_name()

                all_fields = ["title", "content", "submitter", "submitter_date",
                    "group_opinion","group_user", "group_date",
                    "depart_opinion","depart_user", "depart_date",
                    "manager_opinion","manager_user", "manager_date",
                    "final_opinion","final_user", "final_date"]

                fill_fields = []

                if task_name == "Create":
                    fields = all_fields[0:2]
                    static_fields = []
                    fill_fields = ["submitter", "submitter_date"]
                    layout = [
                        ('title'),
                        ('content'),
                    ]

                if task_name == "Group":
                    fields = all_fields[0:5]
                    static_fields = all_fields[0:4]
                    fill_fields = ["group_user", "group_date"]
                    layout = [
                        ('title'),
                        ('content'),
                        ['---']
                        ["submitter", "submitter_date"],
                        ("group_opinion")
                    ]

                if task_name == "Depart":
                    fields = all_fields[0:8]
                    static_fields = all_fields[0:7]
                    fill_fields = ["depart_user", "depart_date"]

                if task_name == "Boss" or task_name == "Manager":
                    fields = all_fields[0:11]
                    static_fields = all_fields[0:10]
                    fill_fields = ["manager_user", "manager_date"]

                if task_name == "Checker":
                    fields = all_fields[0:14]
                    static_fields = all_fields[0:13]
                    fill_fields = ["final_user", "final_date"]

                if task_name == "Archiver":
                    fields = all_fields[0:16]
                    static_fields = all_fields[0:16]

                def pre_save(obj, data):
                    if fill_fields:
                        data[fill_fields[0]] = request.user.id
                        data[fill_fields[1]] = datetime.datetime.now()

                view = EditView(self.model, url_for(self.__class__.view, id=id),
                    fields=fields, static_fields = static_fields,
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
        #from uliweb.utils.generic import EditView

        obj = self.model.get(int(id))

        fields = ['title','content','submitter','submitter_date']
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

        data = {
            'detailview': result['view'],
            'obj': result['object'],
            'workflow': helper.get_workflow(),
        }

        tasks = helper.get_active_tasks()

        if len(tasks) == 1:
            task_id = tasks[0].get_unique_id()
            fields = [{'name': 'trans_message', 'verbose_name':'流转意见'}]

            if helper.has_deliver_permission(tasks[0], request.user):
                next_tasks = tasks[0].get_next_tasks()
                form = get_deliver_form(tasks[0], next_tasks)

                data.update({
                    'deliverform': form,
                    'show_deliver_form':True,
                    'task_desc': tasks[0].get_desc(),
                    'task_spec_name': tasks[0].get_spec_name()
                })

            else:
                data.update({
                    'show_deliver_form':False,
                    'task_desc': tasks[0].get_desc(),
                    'task_spec_name': tasks[0].get_spec_name()
                })

        else:
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




