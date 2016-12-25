# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api


class MingjingNews(BrowserView):

    template = ViewPageTemplateFile('template/mingjing_news.pt')

    def __call__(self):
        context = self.context
        request = self.request

        return self.template()
