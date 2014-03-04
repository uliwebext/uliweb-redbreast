#coding=utf8
class ApproveEditForm(object):

    all_fields = ["title", "content", "submitter", "submitter_date",
        "group_opinion","group_user", "group_date",
        "depart_opinion","depart_user", "depart_date",
        "manager_opinion","manager_user", "manager_date",
        "final_opinion","final_user", "final_date"]

    class CreateForm(object):
        fields = ["title", "content"]
        layout = [
            '-- 申请信息 --',
            ("title"), ("content"),
        ]
        static_fields = []
        auto_fill_fields = ["submitter", "submitter_date"]

    class GroupForm(object):
        fields = [
            "title", "content",
            "submitter", "submitter_date",
            "group_opinion"
        ]
        layout = [
            '-- 申请信息 --',
            ("title"), ("content"),
            ("submitter", "submitter_date"),
            '-- 小组内部审批 --',
            ("group_opinion"),
        ]
        auto_fill_fields = ["group_user", "group_date"]

    class DepartForm(object):
        fields = [
            "title", "content",
            "submitter", "submitter_date",
            "group_opinion","group_user", "group_date",
            "depart_opinion",
        ]
        layout = [
            '-- 申请信息 --',
            ("title"), ("content"),
            ("submitter", "submitter_date"),
            '-- 小组内部审批 --',
            ("group_opinion"),
            ("group_user", "group_date"),
            '-- 部门审批 --',
            ("depart_opinion"),
        ]
        auto_fill_fields = ["depart_user", "depart_date"]

    class ManagerForm(object):
        fields = [
            "title", "content",
            "submitter", "submitter_date",
            "group_opinion","group_user", "group_date",
            "depart_opinion","depart_user", "depart_date",
            "manager_opinion",
        ]
        layout = [
            '-- 申请信息 --',
            ("title"), ("content"),
            ("submitter", "submitter_date"),
            '-- 小组内部审批 --',
            ("group_opinion"),
            ("group_user", "group_date"),
            '-- 部门审批 --',
            ("depart_opinion"),
            ("depart_user", "depart_date"),
            '-- 领导审批 --',
            ("manager_opinion"),
        ]
        auto_fill_fields = ["manager_user", "manager_date"]

    class BossForm(object):
        fields = [
            "title", "content",
            "submitter", "submitter_date",
            "group_opinion","group_user", "group_date",
            "depart_opinion","depart_user", "depart_date",
            "manager_opinion",
        ]
        layout = [
            '-- 申请信息 --',
            ("title"), ("content"),
            ("submitter", "submitter_date"),
            '-- 小组内部审批 --',
            ("group_opinion"),
            ("group_user", "group_date"),
            '-- 部门审批 --',
            ("depart_opinion"),
            ("depart_user", "depart_date"),
            '-- 领导审批 --',
            ("manager_opinion"),
        ]
        auto_fill_fields = ["manager_user", "manager_date"]

    class CheckerForm(object):
        fields = [
            "title", "content",
            "submitter", "submitter_date",
            "group_opinion","group_user", "group_date",
            "depart_opinion","depart_user", "depart_date",
            "manager_opinion","manager_user", "manager_date",
            "final_opinion",
        ]
        layout = [
            '-- 申请信息 --',
            ("title"), ("content"),
            ("submitter", "submitter_date"),
            '-- 小组内部审批 --',
            ("group_opinion"),
            ("group_user", "group_date"),
            '-- 部门审批 --',
            ("depart_opinion"),
            ("depart_user", "depart_date"),
            '-- 领导审批 --',
            ("manager_opinion"),
            ("manager_user", "manager_date"),
            '-- 审核意见 --',
            ("final_opinion"),
        ]
        auto_fill_fields = ["final_user", "final_date"]

    class ArchiverForm(object):
        fields = [
            "title", "content",
            "submitter", "submitter_date",
            "group_opinion","group_user", "group_date",
            "depart_opinion","depart_user", "depart_date",
            "manager_opinion","manager_user", "manager_date",
            "final_opinion","final_user", "final_date"
        ]
        layout = [
            '-- 申请信息 --',
            ("title"), ("content"),
            ("submitter", "submitter_date"),
            '-- 小组内部审批 --',
            ("group_opinion"),
            ("group_user", "group_date"),
            '-- 部门审批 --',
            ("depart_opinion"),
            ("depart_user", "depart_date"),
            '-- 领导审批 --',
            ("manager_opinion"),
            ("manager_user", "manager_date"),
            '-- 审核意见 --',
            ("final_opinion"),
            ("final_user", "final_date"),
        ]
        auto_fill_fields = []

    def get_form(self, task):
        if hasattr(self, task + "Form"):
            return getattr(self, task + "Form")
