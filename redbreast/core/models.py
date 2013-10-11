#coding=utf-8

from uliweb.orm import *

class Workflow_Spec(Model):
    name = Field(CHAR, verbose_name='工作流名称', max_length=255, required=True, unique=True)
    content = Field(PICKLE, verbose_name='工作流定义内容')
    
class Task_Spec(Model):
    name = Field(CHAR, verbose_name='工作流活动名称', max_length=255, required=True, unique=True)
    content = Field(PICKLE, verbose_name='活动定义内容')
    
