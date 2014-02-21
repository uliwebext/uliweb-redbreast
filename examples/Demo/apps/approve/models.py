#coding=utf8
from uliweb.orm import *

class Approve(Model):
    title = Field(str, max_length=80, verbose_name='标题')
    content = Field(TEXT, verbose_name='审批内容')
    submitter = Reference('user', verbose_name='提交人')
    group_opinion = Field(TEXT, verbose_name='小组意见')
    group_user = Reference('user', verbose_name='小组意见填写人')
    depart_opinion = Field(TEXT, verbose_name='部门意见')
    depart_user = Reference('user', verbose_name='部门意见填写人')
    manager_opinion = Field(TEXT, verbose_name='领导意见')
    manager_user = Reference('user', verbose_name='领导意见填写人')
    final_opinion = Field(TEXT, verbose_name='最终审核意见')
    final_user = Reference('user', verbose_name='最终审核意见填写人')
    
    def __unicode__(self):
        return self.title