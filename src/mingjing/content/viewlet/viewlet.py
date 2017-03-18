# -*- coding: utf-8 -*-
from plone.app.layout.viewlets import common as base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
import MySQLdb
from DateTime import DateTime
from datetime import datetime

LIMIT = 10


class HotHit(base.ViewletBase):

    def update(self):
        context = self.context
        portal = api.portal.get()
        request = self.request

        dbSetting = api.portal.get_registry_record('mingjing.content.browser.mjnetSetting.IMJNetSetting.mysqlSetting')
        host, port, userName, password, dbName, charset = dbSetting.split(',')
        port = int(port)
        db = MySQLdb.connect(host=host, port=port, user=userName, passwd=password, db=dbName, charset=charset)
        cursor = db.cursor()

        range = [0.5, 1, 2, 3, 7, 30]
        self.brain = []
        for date in range:
            startDate = DateTime() - date
            sqlStr = "SELECT `uid` FROM `mj_counter` WHERE `created` > '%s' ORDER BY `mj_counter`.`viewCounter` DESC LIMIT 10" % \
                     startDate.strftime('%Y/%m/%d %H:%M:%S')
            cursor.execute(sqlStr)
            results = cursor.fetchall()
            uids = []
            for item in results:
                uids.append(item[0])

            self.brain.append(api.content.find(context=portal, UID=uids, sort_limit=LIMIT)[:LIMIT])


class ViewCounter(base.ViewletBase):

    def update(self):
        context = self.context
        uid = context.UID()
        created = context.created().strftime('%Y/%m/%d %H:%M:%S')

        dbSetting = api.portal.get_registry_record('mingjing.content.browser.mjnetSetting.IMJNetSetting.mysqlSetting')
        host, port, userName, password, dbName, charset = dbSetting.split(',')
        port = int(port)
        db = MySQLdb.connect(host=host, port=port, user=userName, passwd=password, db=dbName, charset=charset)
        cursor = db.cursor()

        sqlStr = "INSERT INTO mj_counter(uid, created, viewCounter) VALUES ('%s', '%s', 1) \
                 ON DUPLICATE KEY UPDATE viewCounter = viewCounter +1;" % (uid, created)
        cursor.execute(sqlStr)
        db.commit()
        db.close()


class RwdMenu(base.ViewletBase):
    """  """


class ScriptToFooter(base.ViewletBase):
    """  """


class AboveContentInfo(base.ViewletBase):
    """  """


class SocialList(base.ViewletBase):
    """  """


class CustomInfoInHeader(base.ViewletBase):
    """  """

    def render(self):
        portal = api.portal.get()
        request = self.request
        context = self.context
        to_folder_contents = True if ('edit' in request.get('HTTP_REFERER') and context.Type() not in ['Folder', 'Plone Site']) else False

        if to_folder_contents:
#            return '<script>document.location.href="%s/folder_contents";</script>' % context.getParentNode().absolute_url()
            return '<meta http-equiv="refresh" content="0;url=%s/folder_contents" />' % context.getParentNode().absolute_url()
        return ''
