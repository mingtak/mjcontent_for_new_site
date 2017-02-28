
# -*- coding: utf-8 -*-

import sys
from Testing import makerequest
from AccessControl.SecurityManagement import newSecurityManager
from zope.site.hooks import setHooks
from zope.site.hooks import setSite

from plone import api
from DateTime import DateTime
import transaction
import csv
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from bs4 import BeautifulSoup
from Products.CMFPlone.utils import safe_unicode
from plone.app.textfield.value import RichTextValue
from plone import namedfile
#import html2text
import urllib2
import logging
import json
import MySQLdb

# howto: bin/client1 run pathtofile/import_news.py portal_name admin_id news_site_code(ex. bbc)
# mapping: sys.argv[3] is portal_name, sys.argv[4] is admin_id, sys.argv[5] is news_site_code
#          sys.argv[6] is dataType, 'xml', 'html' ...

news_site_code = {
    'sql':'sql'
}

logger = logging.getLogger('Import News')


class ImportContents:

    def __init__(self, portal, admin, news_site, dataType):
        root = makerequest.makerequest(app)
        self.portal = getattr(root, portal, None)
        self.news_site = news_site_code.get(news_site, None)
        if self.portal is None or self.news_site is None:
            logger.error('lost or wrong argv!')
            exit()

        admin = root.acl_users.getUserById(admin)
        admin = admin.__of__(self.portal.acl_users)
        newSecurityManager(None, admin)
        setHooks()
        setSite(self.portal)
        self.portal.setupCurrentSkin(self.portal.REQUEST)

        self.dataType = dataType


    def getDocs(self, site_code, dataType):
        portal = self.portal
        request = self.portal.REQUEST
        catalog = portal.portal_catalog
        alsoProvides(request, IDisableCSRFProtection)

        if dataType == 'video':
            self.importVideo(site_code)
        if dataType == 'blog':
            self.importBlog(site_code)
        if dataType == 'news':
            self.importNews(site_code)
        if dataType == 'mag':
            self.importMag(site_code)

        transaction.commit()
        return


    def importVideo(self, site_code):
        portal = self.portal
        request = self.portal.REQUEST
        alsoProvides(request, IDisableCSRFProtection)

        # 建立DB 連線資訊定設定中文編碼utf-8
        db = MySQLdb.connect("localhost","mibdb","mibdb","mibdb",charset='utf8')
        cursor = db.cursor()
        sql_video = "SELECT * FROM `vo_video` WHERE `CreateTime` > '2016-12-01 00:00:00'"

        cursor.execute(sql_video)
        old_video = cursor.fetchall()
        count = 0
        print 'TOTAL: %s' % len(old_video)
        import pdb; pdb.set_trace()
        for item in old_video:
            old_ID = item[1]
            if api.content.find(context=portal['video'], id=old_ID):
                continue

            old_TypeID = item[6]
            old_Title = item[12]
            old_YoutubeURL = item[14]
            old_PicturePath = item[15]
            old_Keywords = item[17]
            old_Description = item[18]
            old_CreateTime = item[43]

            sql_Content = "SELECT * FROM `vo_videocontents` WHERE `VideoID` = '%s'" % old_ID
            cursor.execute(sql_Content)
            old_RichText = cursor.fetchall()[0][1]
            if old_TypeID and portal['video'].get(old_TypeID.lower()):
                newContent = api.content.create(
                    container=portal['video'].get(old_TypeID.lower()),
                    type='Youtube',
                    id=old_ID,
                    title=old_Title,
                    description=old_Description,
                    oldPicturePath=old_PicturePath,
                    oldCreateTime=old_CreateTime,
                    oldKeywords=old_Keywords,
                    text=RichTextValue(old_RichText),
                    youtubeURL=old_YoutubeURL,
                )
#                old_Keywords.append(portal['video'][old_TypeID.lower()].title)
#                newContent.setSubject(tuple(old_Keywords))

                api.content.transition(obj=newContent, transition='publish')
                newContent.reindexObject()
                count += 1
                print count
                if count % 10 == 0:
                    transaction.commit()
            else:continue

        db.close()


    def importBlog(self, site_code):
        portal = self.portal
        request = self.portal.REQUEST
        alsoProvides(request, IDisableCSRFProtection)

        # 建立DB 連線資訊定設定中文編碼utf-8
        db = MySQLdb.connect("localhost","mibdb","mibdb","mibdb",charset='utf8')
        cursor = db.cursor()
        sql_blog = "SELECT * FROM `bg_blog` WHERE `CreateTime` > '2016-12-01 00:00:00'"

        cursor.execute(sql_blog)
        old_blog = cursor.fetchall()
        count = 0
        print 'TOTAL: %s' % len(old_blog)
        import pdb; pdb.set_trace()
        for item in old_blog:
            old_BlogID = item[0]
            if api.content.find(context=portal['blog'], id=old_BlogID):
                continue

            old_BlogTypeID = item[1]
            old_Title = item[5]
            old_PicturePath = item[8]
            old_ArticleContents = item[11]
            old_CreateTime = item[24]

            sql_blogContent = "SELECT * FROM `bg_blogcontents` WHERE `BlogID` = '%s'" % old_BlogID
            cursor.execute(sql_blogContent)
            old_RichText = cursor.fetchall()[0][1]
            if old_BlogTypeID and portal['blog'].get(old_BlogTypeID):
                newContent = api.content.create(
                    container=portal['blog'].get(old_BlogTypeID),
                    type='Blog',
                    id=old_BlogID,
                    title=old_Title,
                    description=old_ArticleContents,
                    oldPicturePath=old_PicturePath,
                    oldCreateTime=old_CreateTime,
                    text=RichTextValue(old_RichText),
                )
                api.content.transition(obj=newContent, transition='publish')
                newContent.reindexObject()
                count += 1
                print count
                if count % 10 == 0:
                    transaction.commit()
            else:continue

        db.close()


    def importNews(self, site_code):
        portal = self.portal
        request = self.portal.REQUEST
        alsoProvides(request, IDisableCSRFProtection)
        try:
            # 建立DB 連線資訊定設定中文編碼utf-8
            db = MySQLdb.connect("localhost","mibdb","mibdb","mibdb",charset='utf8')
            sql_newsType = "SELECT * FROM `ns_type`"
            # 執行SQL statement
            cursor = db.cursor()
            cursor.execute(sql_newsType)
            old_newsType = cursor.fetchall()
            new_newsType = {}
            for item in old_newsType:
                new_newsType[item[1]] = item[2]
#            import pdb;pdb.set_trace()


            sql_getNews = "SELECT * FROM `ns_news` WHERE `CreateTime` > '2016-12-01 00:00:00' ORDER BY `ns_news`.`NewsDate` ASC"
            cursor.execute(sql_getNews)
            # 撈取多筆資料
            results = cursor.fetchall()
            # 迴圈撈取資料
            count = 0
            print 'TOTAL: %s' % len(results)
#            import pdb; pdb.set_trace()
            for record in results:
                old_NewsId = record[1]
                if api.content.find(context=portal['news'], id=old_NewsId):
                    continue

                old_NewsTypeID = record[5]
                old_Title = record[8]
                old_PicturePath = record[12]
                old_KeyWord = record[14]
                old_NewsContents = record[15]
                old_CreateTime = record[31]

                sql_2 = "SELECT * FROM `ns_newscontents` WHERE `NewsID` = '%s'" % old_NewsId
                cursor.execute(sql_2)
                old_NewsContents = cursor.fetchall()[0][1]
#                print '=========================================\n'
#                print '%s, %s, %s, %s, %s, %s, %s, %s' % (old_NewsId, old_NewsTypeID, old_Title, old_PicturePath, old_KeyWord, old_NewsContents, old_CreateTime, old_NewsContents)
                if old_NewsTypeID in new_newsType:
#                    import pdb; pdb.set_trace()
                    try:
                        newContent = api.content.create(
                            container=portal['news'][old_NewsTypeID.lower()],
                            type='News Item',
                            id=old_NewsId,
                            title=old_Title,
                            description=old_Title,
                            oldPicturePath=old_PicturePath,
                            oldKeywords=old_KeyWord,
                            oldCreateTime=old_CreateTime,
                            freeContent=RichTextValue(old_NewsContents),
                            text=RichTextValue(old_NewsContents),
                        )
                    except:
                        continue
                    subject = old_KeyWord.split(',')
                    subject.append(portal['news'][old_NewsTypeID.lower()].title)
                    newContent.setSubject(tuple(subject))
                    api.content.transition(obj=newContent, transition='publish')
                    newContent.reindexObject()
                    count += 1
                    print count
                    if count % 10 == 0:
                        transaction.commit()
#                    import pdb; pdb.set_trace()
#                    break
            db.close()
#            import pdb; pdb.set_trace()
        except MySQLdb.Error as e:
            print "Error %d: %s" % (e.args[0], e.args[1])


instance = ImportContents(sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
instance.getDocs(sys.argv[5], sys.argv[6])



