#coding=utf-8

class WFBasicLayout(object):

    BEFORE_HTML = ""
    AFTER_HTML = ""

    def __init__(self, items):
        self._items = items

    def before_html(self):
        return self.BEFORE_HTML

    def after_html(self):
        return self.AFTER_HTML

    def html(self):
        output = [self.before_html()]
        for index, item in enumerate(self._items):
            data = self.process(index, item)
            output.append(self.one(data))
        output.append(self.after_html())
        return "".join(output)

    def process(self, index, item):
        return item

    def get_one(self, data):
        return str(data)


class WFTransListLayout(WFBasicLayout):
    BEFORE_HTML = "<ul>"
    AFTER_HTML = "</ul>"

    def process(self, index, item):
        return {
            'order': index + 1,
            'from_task': item.from_name,
            'to_task': item.to_name,
            'created_user': item.created_user,
            'created_date': item.created_date,
            'message': item.message
        }

    def one(self, data):
        text = "<li>From %(from_task)s to %(to_task)s, by %(created_user)s at %(created_date)s.</li>" % data
        return text

class WFTransBoxLayout(WFTransListLayout):
    BEFORE_HTML = "<div class='wf-trans-list box-style'>"
    AFTER_HTML = "</div>"

    def one(self, data):
        if not data['message']:
            data['message'] = u"<i>未填写</i>"

        if data['from_task'] and data['to_task']:
            operation = u" 执行从<span class='task'>【%(from_task)s】</span>到<span class='task'>【%(to_task)s】</span>的流转操作，"
        elif data['to_task']:
            operation = u" 创建活动<span class='task'>【%(to_task)s】</span>，"
        elif data['from_task']:
            operation = u" 在活动<span class='task'>【%(from_task)s】</span>执行办结操作，"

        text = [
            u"<div class='item'>",
                u"<div class='order'>%(order)s</div>",
                u"<div class='info'>",
                    u"<span class='create_user'>%(created_user)s</span> 于 <span class='create_date'>%(created_date)s</span>",
                    operation,
                u"</div>",
                u"<div class='trans_message'>流转意见为： %(message)s </div>"
            u"</div>",
        ]

        return "".join(text) % data
