#coding=utf-8

from uliweb.orm import *

class Workflow_Spec(Model):
    """
    工作流定义表
    """
    name = Field(CHAR, verbose_name='工作流名称', max_length=255, required=True, unique=True)
    content = Field(PICKLE, verbose_name='工作流定义内容')
    source = Field(str, max_length=255, verbose_name='定义文件名')
    created_date = Field(datetime.datetime, verbose_name='创建时间', auto_now_add=True)
    modified_date = Field(datetime.datetime, verbose_name='修改时间', auto_now=True, auto_now_add=True)
    
class Task_Spec(Model):
    """
    工作流活动定义表
    """
    name = Field(CHAR, verbose_name='工作流活动名称', max_length=255, required=True, unique=True)
    content = Field(PICKLE, verbose_name='活动定义内容')
    source = Field(str, max_length=255, verbose_name='定义文件名')
    created_date = Field(datetime.datetime, verbose_name='创建时间', auto_now_add=True)
    modified_date = Field(datetime.datetime, verbose_name='修改时间', auto_now=True, auto_now_add=True)
    
