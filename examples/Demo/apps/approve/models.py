#coding=utf8
from uliweb.orm import *
import datetime

class Approve(Model):
    title = Field(str, max_length=80, verbose_name='标题', required=True)
    content = Field(TEXT, verbose_name='审批内容', required=True)
    submitter = Reference('user', verbose_name='提交人')
    submitter_date = Field(datetime.datetime, verbose_name='提交时间')

    group_opinion = Field(TEXT, verbose_name='小组意见')
    group_user = Reference('user', verbose_name='小组意见填写人')
    group_date = Field(datetime.datetime, verbose_name='小组填写时间')

    depart_opinion = Field(TEXT, verbose_name='部门意见')
    depart_user = Reference('user', verbose_name='部门意见填写人')
    depart_date = Field(datetime.datetime, verbose_name='部门填写时间')

    manager_opinion = Field(TEXT, verbose_name='领导意见')
    manager_user = Reference('user', verbose_name='领导意见填写人')
    manager_date = Field(datetime.datetime, verbose_name='领导填写时间')

    final_opinion = Field(TEXT, verbose_name='最终审核意见')
    final_user = Reference('user', verbose_name='最终审核意见填写人')
    final_date = Field(datetime.datetime, verbose_name='最终审核时间')

    workflow_status = Field(str, max_length=255, verbose_name="当前阶段")

    workflow = Reference('workflow', verbose_name='关联工作流', collection_name='approves')

    def __unicode__(self):
        return self.title

    class AddForm:
        fields = [
            'title',
            'content',
        ]

    class EditForm:
        fields = [
            'title',
            'content',
        ]

    class Table:
        fields = [
            {'name':'title', 'width':250, 'sortable':True},
            {'name':'content', 'width':100, 'sortable':True},
            {'name':'workflow_status', 'width':100, 'sortable':True},
            {'name':'submitter', 'width':100, 'sortable':True},
            {'name':'submitter_date', 'width':100, 'sortable':True},
        ]

