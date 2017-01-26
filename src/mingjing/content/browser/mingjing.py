# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api


class MingjingFolder(BrowserView):

    def __call__(self):
        return self.template()


class MingjingNews(MingjingFolder):
    template = ViewPageTemplateFile('template/mingjing_news.pt')


class MingjingTv(MingjingFolder):
    template = ViewPageTemplateFile('template/mingjing_tv.pt')


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
