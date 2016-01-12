# -*- coding:utf-8 -*-
from tornado.web import RequestHandler

__author__ = 'george'


class HelloHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('miniui/index.html')


class HomeHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('miniui/home.html')


class MenuHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('miniui/menu.add.html')
        #         menu_info="""﻿[
        # 	{id: "user", text: "用户管理"},
        #
        # 	{id: "lists", text: "Lists", pid: "user" },
        #
        # 	{id: "datagrid", text: "DataGrid", pid: "lists"},
        # 	{id: "tree", text: "Tree" , pid: "lists"},
        # 	{id: "treegrid", text: "TreeGrid " , pid: "lists"},
        #
        # 	{id: "layouts", text: "Layouts", pid: "user"},
        #
        # 	{id: "panel", text: "Panel", pid: "layouts"},
        # 	{id: "splitter", text: "Splitter", pid: "layouts"},
        # 	{id: "layout", text: "Layout ", pid: "layouts"},
        #
        # 	{ id: "right", text: "权限管理"},
        #
        # 	{id: "base", text: "Base",  pid: "right" },
        #
        # 	{id: "ajax", text: "Ajax", pid: "base"},
        # 	{id: "json", text: "JSON", pid: "base"},
        # 	{id: "date", text: "Date", pid: "base"},
        #
        # 	{id: "forms", text: "Forms", pid: "right"},
        #
        # 	{id: "button", text: "Button", pid: "forms"},
        # 	{id: "listbox", text: "ListBox", pid: "forms"},
        # 	{id: "checkboxlist", text: "CheckBoxList", pid: "forms"},
        # 	{id: "radiolist", text: "RadioList", pid: "forms"},
        # 	{id: "calendar", text: "Calendar", pid: "forms"}
        # ]"""
        #         self.write(menu_info)

    def post(self, *args, **kwargs):
        pass


routes = [
    (r'/miniui/', HelloHandler),
    (r'/miniui$', HelloHandler),
    (r'/miniui/home', HomeHandler),
    (r'/miniui/menu', MenuHandler),
]
