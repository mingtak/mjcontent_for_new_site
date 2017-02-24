# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
import json
from datetime import datetime


class MingjingFolder(BrowserView):

    def __call__(self):
        return self.template()


class MingjingNews(MingjingFolder):
    template = ViewPageTemplateFile('template/mingjing_news.pt')


class MingjingTv(MingjingFolder):
    template = ViewPageTemplateFile('template/mingjing_tv.pt')

    def liveProgram(self, jsonString):
        context = self.context
        liveProgram = json.loads(jsonString)
#        startTime = datetime.fromtimestamp(liveProgram['startTime'])
        startTime = int(liveProgram['startTime'])
        for item in liveProgram['pl']:
            item['start'] = datetime.fromtimestamp(startTime)
            item['end'] = datetime.fromtimestamp(startTime+item['during'])
            startTime += item['during']
        return liveProgram['pl']


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
