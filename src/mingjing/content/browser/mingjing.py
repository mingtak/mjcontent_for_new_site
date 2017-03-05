# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
import json
from datetime import datetime
import transaction
from .views import CoverView


class MingjingFolder(BrowserView):

    def __call__(self):
        return self.template()


class MingjingNews(MingjingFolder):
    template = ViewPageTemplateFile('template/mingjing_news.pt')


class MingjingTv(MingjingFolder):
    template = ViewPageTemplateFile('template/mingjing_tv.pt')

    def liveProgram(self, jsonString):

        pl = CoverView(self, BrowserView)
        return pl.liveProgram(jsonString)

        """
        context = self.context
        liveProgram = json.loads(jsonString)
        startTime = int(liveProgram['startTime'])
        for item in liveProgram['pl']:
            item['start'] = datetime.fromtimestamp(startTime)
            item['end'] = datetime.fromtimestamp(startTime+item['during'])
            startTime += item['during']
        return liveProgram['pl'] """


class MingjingMag(MingjingFolder):
    template = ViewPageTemplateFile('template/mingjing_mag.pt')


class MingjingBlog(MingjingFolder):
    template = ViewPageTemplateFile('template/mingjing_blog.pt')


class MingjingPub(MingjingFolder):
    template = ViewPageTemplateFile('template/mingjing_pub.pt')


class MingjingBook(MingjingFolder):
    template = ViewPageTemplateFile('template/mingjing_book.pt')


class MingjingEbook(MingjingFolder):
    template = ViewPageTemplateFile('template/mingjing_ebook.pt')


class SetFeatured(BrowserView):

    def __call__(self):
        portal = api.portal.get()
        request = self.request

        if not request.form.get('uid'):
            return
        brain = api.content.find(context=portal, UID=request.form['uid'])
        try:
            item = brain[0].getObject()
        except:return

        if request.form.get('checked') == 'true':
            item.featured = True
        else:
            item.featured = False
        item.reindexObject(idxs=['featured'])
        transaction.commit()
        return

