#coding=utf-8

from uliweb.orm import *
from uliweb.utils.common import get_var
import datetime

def get_modified_user():
    from uliweb import request
    if request and request.user and request.user.id:
        return request.user.id
    else:
        return None

class Workflow(Model):
    """
    工作流实例表
    """
    spec_name = Field(CHAR, verbose_name='工作流定义标识', max_length=255, required=True)
    desc = Field(CHAR, verbose_name='工作流显示名称', max_length=255)
    state = Field(int, verbose_name='工作流状态', default=1, choices=get_var('PARA/WF_STATUS'), index=True)
    created_date = Field(datetime.datetime, verbose_name='创建时间', auto_now_add=True)
    created_user = Reference('user', verbose_name='创建人', default=get_modified_user, auto_add=True)
    modified_date = Field(datetime.datetime, verbose_name='修改时间', auto_now=True, auto_now_add=True)
    modified_user = Reference('user', verbose_name='修改人', default=get_modified_user, auto=True, auto_add=True)
    data = Field(PICKLE, verbose_name='工作流绑定数据')
    ref_unique_id = Field(CHAR, verbose_name='关联数据标识', max_length=255)
    

class Workflow_Task(Model):
    """
    工作流活动实例表
    """
    workflow = Reference('workflow', verbose_name='所属工作流', collection_name="tasks", index=True)
    spec_name = Field(CHAR, verbose_name='活动定义名称', max_length=255)
    desc = Field(CHAR, verbose_name='活动显示名称', max_length=255)
    alias_name = Field(CHAR, verbose_name='活动名称', max_length=255)
    state = Field(int, verbose_name='活动状态', default=1, choices=get_var('PARA/WF_TASK_STATUS'))
    created_date = Field(datetime.datetime, verbose_name='创建时间', auto_now_add=True)
    created_user = Reference('user', verbose_name='创建人')
    modified_date = Field(datetime.datetime, verbose_name='修改时间')
    modified_user = Reference('user', verbose_name='修改人')
    data = Field(PICKLE, verbose_name='工作流活动绑定数据')
    uuid = Field(CHAR, verbose_name='UUID', max_length=255)
    async_deliver_date = Field(datetime.datetime, auto_now=True, auto_now_add=True)
    async_deliver_try_count = Field(int, default=0)

class Workflow_Trans(Model):
    """
    工作流活动流向表
    """
    workflow = Reference('workflow', verbose_name='所属工作流', collection_name="trans", index=True)
    from_task = Reference('workflow_task', verbose_name='流出活动', collection_name="child_tasks")
    to_task = Reference('workflow_task', verbose_name='流入活动', collection_name="parent_tasks")
    from_name = Field(CHAR, verbose_name='前点名称', max_length=255)
    to_name = Field(CHAR, verbose_name='终点名称', max_length=255)
    created_date = Field(datetime.datetime, verbose_name='创建时间', auto_now_add=True)
    created_user = Reference('user', verbose_name='创建人')
    message = Field(CHAR, verbose_name='流转意见', max_length=255)
    type = Field(int, verbose_name='流向类型', choices=get_var('PARA/WF_TRANS_TYPE'), default=2)

