# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
import MySQLdb
import json
from datetime import datetime
from DateTime import DateTime
import transaction
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from .views import CoverView

LIMIT = 20


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

        if request.form.has_key('checked'):
            if request.form.get('checked') == 'true':
                item.featured = True
            else:
                item.featured = False
            notify(ObjectModifiedEvent(item))
            item.reindexObject()
        elif request.form.has_key('headWeight'):
            item.headWeight = int(request.form.get('headWeight', 10))
            notify(ObjectModifiedEvent(item))
            item.reindexObject()
        transaction.commit()
        return


class Ranking(BrowserView):
    template = ViewPageTemplateFile('template/ranking.pt')

    def __call__(self):

        self.portal = api.portal.get()
        request = self.request

        dbSetting = api.portal.get_registry_record('mingjing.content.browser.mjnetSetting.IMJNetSetting.mysqlSetting')
        host, port, userName, password, dbName, charset = dbSetting.split(',')
        port = int(port)
        db = MySQLdb.connect(host=host, port=port, user=userName, passwd=password, db=dbName, charset=charset)
        cursor = db.cursor()

        range = request.form.get('range', '1d')
        if range == '1d':
            range = DateTime() - 1
        elif range == '2d':
            range = DateTime() - 2
        elif range == '3d':
            range = DateTime() - 3
        elif range == 'w':
            range = DateTime() - 7
        elif range == 'm':
            range = DateTime() - 30
        elif range == '12h':
            range = DateTime() - 0.5
        elif range == 'newest':
            range = DateTime() - 0.3
        elif range == 'head':
            range = DateTime() - 1.5
        elif range == 'editor':
            range = DateTime() - 2.5
        elif range == 'hot':
            range = DateTime() - 0.8
        elif range == 'world':
            range = DateTime() - 5
        else:
            range = DateTime() - 1

        sqlStr = "SELECT `uid` FROM `mj_counter` WHERE `created` > '%s' ORDER BY `mj_counter`.`viewCounter` DESC LIMIT 20" % \
                 range.strftime('%Y/%m/%d %H:%M:%S')
        cursor.execute(sqlStr)
        results = cursor.fetchall()
        uids = []
        for item in results:
            uids.append(item[0])

        self.brain = api.content.find(context=self.portal, UID=uids, sort_limit=LIMIT)[:LIMIT]
        db.close()
        return self.template()


class RssRanking(Ranking):
    template = ViewPageTemplateFile('template/rss_ranking.pt')


class HotHits(BrowserView):

    def __call__(self):
        portal = api.portal.get()
        request = self.request

        dbSetting = api.portal.get_registry_record('mingjing.content.browser.mjnetSetting.IMJNetSetting.mysqlSetting')
        host, port, userName, password, dbName, charset = dbSetting.split(',')
        port = int(port)
        db = MySQLdb.connect(host=host, port=port, user=userName, passwd=password, db=dbName, charset=charset)
        cursor = db.cursor()

        range = [0.5, 1, 2, 3, 7, 30]
        brain = []
        for date in range:
            startDate = DateTime() - date
            sqlStr = "SELECT `uid` FROM `mj_counter` WHERE `created` > '%s' ORDER BY `mj_counter`.`viewCounter` DESC LIMIT 10" % \
                     startDate.strftime('%Y/%m/%d %H:%M:%S')
            cursor.execute(sqlStr)
            results = cursor.fetchall()
            uids = []
            for item in results:
                uids.append(item[0])

            brain.append(api.content.find(context=portal, UID=uids, sort_limit=LIMIT)[:LIMIT])
        return brain

