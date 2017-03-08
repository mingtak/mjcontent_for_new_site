# -*- coding: utf-8 -*-
from plone.app.layout.viewlets import common as base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
import MySQLdb
from DateTime import DateTime
from datetime import datetime


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
