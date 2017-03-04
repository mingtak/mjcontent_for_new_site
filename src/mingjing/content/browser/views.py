# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from datetime import datetime
import json
from plone.memoize import ram
from time import time
from Products.CMFPlone.utils import safe_unicode


class ToYoutube(BrowserView):

    def __call__(self):
        context = self.context
        request = self.request
        request.response.redirect(context.youtubeURL)
        return


class CoverView(BrowserView):

    template = ViewPageTemplateFile("template/cover_view.pt")

    #@ram.cache(lambda *args: time() // (120))
    def mainSliderNews(self):
        context = self.context
#        return api.content.find(Type='News Item', id=context.mainSliderNews.split(), sort_on='modified', sort_order='reverse')
        return api.content.find(Type='News Item', sort_on='created', sort_order='reverse')


    #@ram.cache(lambda *args: time() // (120))
    def youtubes(self):
        portal = api.portal.get()
        return api.content.find(context=portal, Type='Youtube', featured=True, sort_on='created', sort_order='reverse')


    #@ram.cache(lambda *args: time() // (120))
    def todayNews(self):
        portal = api.portal.get()
        return api.content.find(context=portal, Type='News Item', featured=True, sort_on='created', sort_order='reverse')


    #@ram.cache(lambda *args: time() // (120))
    def tabsNameLists(self):
        portal = api.portal.get()
        context = self.context
        tabsNameList_1 = context.tabsName.split()[0].encode('utf-8').split(',')
        tabsNameList_2 = context.tabsName.split()[1].encode('utf-8').split(',')
        tabsNameList_3 = context.tabsName.split()[1].encode('utf-8').split(',')

        tabsBrain_1, tabsBrain_2 ,tabsBrain_3 = [], [], []

        for key in tabsNameList_1:
#            import pdb;pdb.set_trace()
            brain = api.content.find(context=portal, Type='News Item', keywords=safe_unicode(key), featured=True, sort_on='created', sort_order='reverse')
            tabsBrain_1.append(brain[0:5])
        for key in tabsNameList_2:
            brain = api.content.find(context=portal, Type='News Item', keywords=safe_unicode(key), featured=True, sort_on='created', sort_order='reverse')
            tabsBrain_2.append(brain[0:5])
        for key in tabsNameList_3:
            brain = api.content.find(context=portal, Type='News Item', keywords=safe_unicode(key), featured=True, sort_on='created', sort_order='reverse')
            tabsBrain_3.append(brain[0:5])
        return [tabsNameList_1, tabsBrain_1, tabsNameList_2, tabsBrain_2, tabsNameList_3, tabsBrain_3]


    #@ram.cache(lambda *args: time() // (120))
    def ebooks(self):
        portal = api.portal.get()
        context = self.context
        newestBook = api.content.find(context=portal, Type='Ebook', id=context.ebooks.split()[0])[0]
        hotestBook = api.content.find(context=portal, Type='Ebook', id=context.ebooks.split()[1])[0]
        eBook = api.content.find(context=portal, Type='Ebook', id=context.ebooks.split()[2])[0]
        return [newestBook, hotestBook, eBook]


    #@ram.cache(lambda *args: time() // (120))
    def rankingNews(self):
        portal = api.portal.get()
        context = self.context
        return api.content.find(context=portal, Type='News Item', featured=True, sort_on='created', sort_order='reverse')


    #@ram.cache(lambda *args: time() // (120))
    def liveProgram(self, jsonString):
        context = self.context
        liveProgram = json.loads(jsonString)
        startTime = int(liveProgram['startTime'])
        for item in liveProgram['pl']:
            item['start'] = datetime.fromtimestamp(startTime)
            item['end'] = datetime.fromtimestamp(startTime+item['during'])
            startTime += item['during']
        return liveProgram['pl']


    def __call__(self):
        context = self.context
        request = self.request
        portal = api.portal.get()

        return self.template()
