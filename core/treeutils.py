# -*- coding:utf-8 -*-
"""==========================================================
|
|
|       creater:george
|       email:15921315347@163.com
|       description:树形结构处理
|
|
|
============================================================="""
from bson import ObjectId
from core import clone_dict

__author__ = 'george'


def to_list(tree,parentid,children_field,id_field,parent_id_field):
    """
    将树形结构的json数组处理成一个常规数组
    :param tree
    :param parentid
    :param children_field
    :param id_field
    :param parent_id_field
    :return []
    """
    result = []
    for node in tree:
        item = clone_dict(node,without=['children'])
        item[parent_id_field] = parentid
        id=item.get('id',None)
        if not id:
            item['id']=ObjectId()
            item['_id']=item['id']
        else:
            item['id']=ObjectId(id)
            item['_id']=item['id']
        result.append(item)
        childrenes = node.get(children_field)
        if childrenes:
            id = item['id'] or ""
            result.extend(to_list(childrenes, id, children_field, id_field, parent_id_field))
    return result
