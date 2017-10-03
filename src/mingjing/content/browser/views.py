# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from datetime import datetime
from DateTime import DateTime
import json
#from plone.memoize import ram
from time import time
from Products.CMFPlone.utils import safe_unicode
import logging

logger = logging.getLogger('mingjing.content')
LIMIT=20


class CollectionNAView(BrowserView):

    template = ViewPageTemplateFile("template/collection_na_view.pt")

    def __call__(self):
        portal = api.portal.get()
        return self.template()


class ShowFeatured(BrowserView):

    template = ViewPageTemplateFile("template/show_featured.pt")

    def __call__(self):
        portal = api.portal.get()
        self.brain = api.content.find(context=portal, featured=True, sort_on='created', sort_order='reverse', sort_limit=LIMIT)[:LIMIT]
        return self.template()


class NewestContents(BrowserView):

    template = ViewPageTemplateFile("template/newest_contents.pt")

    def __call__(self):
        return self.template()


class ToYoutube(BrowserView):

    def __call__(self):
        context = self.context
        request = self.request
        request.response.redirect(context.youtubeURL)
        return


class YoutubeView(BrowserView):

    template = ViewPageTemplateFile("template/youtube_view.pt")

    def __call__(self):
        return self.template()


class BlogView(BrowserView):

    template = ViewPageTemplateFile("template/blog_view.pt")

    def __call__(self):
        return self.template()


class EbookView(BrowserView):

    template = ViewPageTemplateFile("template/ebook_view.pt")

    def __call__(self):
        return self.template()


class CoverView(BrowserView):

    template = ViewPageTemplateFile("template/cover_view.pt")

#    @ram.cache(lambda *args: time() // (120))
    def mainSliders(self):
        context = self.context
        portal = api.portal.get()

        brain = api.content.find(Type=['News Item', 'Blog', 'Ebook', 'Youtube'], review_state='published', hasOldPicture=True,
                                featured=True, created=self.date_range, sort_on='headWeight', sort_order='reverse')
#        import pdb ; pdb.set_trace()
        if not brain or len(brain) < 10:
            brain = api.content.find(Type=['News Item', 'Blog', 'Ebook', 'Youtube'], review_state='published', hasOldPicture=True,
                                     context=portal['n07'], sort_on='created', sort_order='reverse', sort_limit=LIMIT)[:LIMIT]
        return brain


    #@ram.cache(lambda *args: time() // (120))
    def youtubes(self):
        portal = api.portal.get()
        return api.content.find(context=portal, Type='Youtube', featured=True, review_state='published', sort_on='created', sort_order='reverse', sort_limit=LIMIT)[:LIMIT]


    #@ram.cache(lambda *args: time() // (120))
    def todayNews(self):
        portal = api.portal.get()
        brain = api.content.find(context=portal, Type='News Item', hasOldPicture=True, featured=True, review_state='published', sort_on='created', sort_order='reverse', sort_limit=LIMIT)[:LIMIT]
        return brain

    #@ram.cache(lambda *args: time() // (120))
    def tabsNameLists(self):
        portal = api.portal.get()
        context = self.context
        tabsNameList_1 = context.tabsName.split()[0].encode('utf-8').split(',')
        tabsNameList_2 = context.tabsName.split()[1].encode('utf-8').split(',')
        tabsNameList_3 = context.tabsName.split()[1].encode('utf-8').split(',')

        tabsBrain_1, tabsBrain_2 ,tabsBrain_3 = [], [], []

        for key in tabsNameList_1:
            brain = api.content.find(context=portal, Type='News Item', Subject=key, sort_on='created', review_state='published', sort_order='reverse', sort_limit=LIMIT)[:LIMIT]
            tabsBrain_1.append(brain[0:5])
        for key in tabsNameList_2:
            brain = api.content.find(context=portal, Type='News Item', Subject=key, sort_on='created', review_state='published', sort_order='reverse', sort_limit=LIMIT)[:LIMIT]
            tabsBrain_2.append(brain[0:5])
        for key in tabsNameList_3:
            brain = api.content.find(context=portal, Type='News Item', Subject=key, sort_on='created', review_state='published', sort_order='reverse', sort_limit=LIMIT)[:LIMIT]
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
        brain = api.content.find(context=portal, Type='News Item', featured=True, sort_on='created', sort_order='reverse', sort_limit=LIMIT)[:LIMIT]
        return brain


    #@ram.cache(lambda *args: time() // (120))
    def liveProgram(self, jsonString):
        context = self.context
        liveProgram = json.loads(jsonString)
        startTime = int(liveProgram['startTime'])

        while True:
            endTime = startTime
            for item in liveProgram['pl']:
                endTime += item['during']
            if datetime.fromtimestamp(endTime) < datetime.now():
                startTime = endTime + 1
            else:
                break

        for item in liveProgram['pl']:
            item['start'] = datetime.fromtimestamp(startTime)
            item['end'] = datetime.fromtimestamp(startTime+item['during'])
            startTime += item['during']

        while True:
            if liveProgram['pl'][0]['end'] < datetime.now():
                tmp = liveProgram['pl'].pop(0)
                liveProgram['pl'].append(tmp)
            else:
                break

        return liveProgram['pl']


    def __call__(self):
        context = self.context
        request = self.request
        portal = api.portal.get()
        self.date_range = {
            'query': (
                DateTime()-1,
            ),
            'range': 'min',
        }
        return self.template()
