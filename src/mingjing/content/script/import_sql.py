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

news_site_code = { 'sql':'sql' }
DATERANGE = 1

queryTime = (DateTime()-DATERANGE).strftime('%Y-%m-%d %H:00:00')
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

        oldDBValue = api.portal.get_registry_record('mingjing.content.browser.mjnetSetting.IMJNetSetting.oldSiteDB')
#        oldDBValue = api.portal.get_registry_record('mingjing.content.browser.mjnetSetting.IMJNetSetting.mysqlSetting')
        self.host, self.port, self.user, self.passwd, self.db, self.charset = oldDBValue.split(',')


    def getImage(self, url):
        try:
            #直接從ip去捉
            if 'www.mingjingnews.com' in url:
                imgUrl = url.replace('www.mingjingnews.com', self.host)
            elif 'mingjingnews.com' in url:
                imgUrl = url.replace('mingjingnews.com', self.host)
            else:
                imgUrl = url
            imgRaw = urllib2.urlopen(imgUrl, timeout=2)
            img = imgRaw.read()
            return namedfile.NamedBlobImage(data=img, filename=u'image.png')
        except:
            print 'getImage Error: %s' % imgUrl
            return


    def getDocs(self, site_code, dataType, isOld):
        portal = self.portal
        request = self.portal.REQUEST
        catalog = portal.portal_catalog
        alsoProvides(request, IDisableCSRFProtection)

        if dataType == 'video':
            self.importVideo(site_code, isOld)
        if dataType == 'blog':
            self.importBlog(site_code, isOld)
        if dataType == 'news':
            self.importNews(site_code, isOld)
        if dataType == 'book':
            self.importBooks(site_code, isOld)
        transaction.commit()
        return


    def importBooks(self, site_code, isOld):
        # 匯入 出版/書店/電子書刊
        portal = self.portal
        request = self.portal.REQUEST
        alsoProvides(request, IDisableCSRFProtection)

        # 建立DB 連線資訊定設定中文編碼utf-8
        db = MySQLdb.connect(host=self.host, port=int(self.port), user=self.user, passwd=self.passwd, db=self.db, charset=self.charset)
        cursor = db.cursor()
#        sql_books = "SELECT * FROM `bk_book` ORDER BY `bk_book`.`CreateTime` ASC"
        sql_books = "SELECT * FROM `bk_book` WHERE `CreateTime` > '%s' ORDER BY `bk_book`.`CreateTime` ASC " % queryTime
        cursor.execute(sql_books)
        old_books = cursor.fetchall()
        count = 0
        print 'TOTAL: %s' % len(old_books)
#        import pdb; pdb.set_trace()
        for item in old_books:
            old_ID = item[1]
            old_TypeID = item[2]
            if old_TypeID.startswith('A'):
                if api.content.find(context=portal['book'], id=old_ID):
                    continue
                containerFolder = portal['book'][old_TypeID.lower()]
            if old_TypeID.startswith('E'):
                if api.content.find(context=portal['ebook'], id=old_ID):
                    continue
                containerFolder = portal['ebook'][old_TypeID.lower()]
            if old_TypeID.startswith('P'):
                if api.content.find(context=portal['publisher'], id=old_ID):
                    continue
                containerFolder = portal['publisher'][old_TypeID.lower()]

            old_Title = item[3]
            old_PicturePath = 'http://www.mingjingnews.com/MIBM/upimages/Book/%s' % item[23]
            old_Keywords = item[15]
            old_Description = item[3]
            old_CreateTime = item[35]
            old_ebookURL = item[17]
            old_RichText = item[16]

            if old_TypeID and containerFolder:
#                import pdb; pdb.set_trace()
                newContent = api.content.create(
                    container=containerFolder,
                    type='Ebook',
                    id=old_ID,
                    title=old_Title,
                    description=old_Description,
                    oldPicturePath=old_PicturePath,
                    oldCreateTime=old_CreateTime,
#                    oldKeywords=old_Keywords,
                    keywords=old_Keywords,
                    oldEbookURL=old_ebookURL,
                    text=RichTextValue(old_RichText),
                )
#                old_Keywords.append(portal['video'][old_TypeID.lower()].title)
#                newContent.setSubject(tuple(old_Keywords))

#                api.content.transition(obj=newContent, transition='publish')
                oldImage = self.getImage(old_PicturePath)
                if oldImage:
                    newContent.image = oldImage

                newContent.reindexObject()
                count += 1
                print '%s: %s/%s' % (count, containerFolder.absolute_url(), old_ID)
#                break
                if count % 10 == 0:
                    transaction.commit()
            else:continue

        db.close()


    def importVideo(self, site_code, isOld):
        portal = self.portal
        request = self.portal.REQUEST
        alsoProvides(request, IDisableCSRFProtection)

        # 建立DB 連線資訊定設定中文編碼utf-8
        db = MySQLdb.connect(host=self.host, port=int(self.port), user=self.user, passwd=self.passwd, db=self.db, charset=self.charset)
        cursor = db.cursor()
        sql_video = "SELECT * FROM `vo_video` WHERE `CreateTime` > '%s' ORDER BY `vo_video`.`CreateTime` ASC " % queryTime

        cursor.execute(sql_video)
        old_video = cursor.fetchall()
        count = 0
        print 'TOTAL: %s' % len(old_video)
#        import pdb; pdb.set_trace()
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
#                    oldKeywords=old_Keywords,
                    keywords=old_Keywords,
                    text=RichTextValue(old_RichText),
                    youtubeURL=old_YoutubeURL,
                )
#                old_Keywords.append(portal['video'][old_TypeID.lower()].title)
#                newContent.setSubject(tuple(old_Keywords))
                oldImage = self.getImage(old_PicturePath)
                if oldImage:
                    newContent.image = oldImage

                api.content.transition(obj=newContent, transition='publish')
                newContent.reindexObject()
                count += 1
                print count
                if count % 10 == 0:
                    transaction.commit()
            else:continue

        db.close()


    def importBlog(self, site_code, isOld):
        portal = self.portal
        request = self.portal.REQUEST
        alsoProvides(request, IDisableCSRFProtection)

        # 建立DB 連線資訊定設定中文編碼utf-8
        db = MySQLdb.connect(host=self.host, port=int(self.port), user=self.user, passwd=self.passwd, db=self.db, charset=self.charset)
        cursor = db.cursor()
        sql_blog = "SELECT * FROM `bg_blog` WHERE `CreateTime` > '%s' ORDER BY `bg_blog`.`CreateTime` ASC " % queryTime

        cursor.execute(sql_blog)
        old_blog = cursor.fetchall()
        count = 0
        print 'TOTAL: %s' % len(old_blog)
#        import pdb; pdb.set_trace()
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
                try:
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

                    oldImage = self.getImage(old_PicturePath)
                    if oldImage:
                        newContent.image = oldImage

                    newContent.reindexObject()
                    count += 1
                except:
                    continue
                print count
                if count % 10 == 0:
                    transaction.commit()
            else:continue

        db.close()


    # 匯入 新聞 / 雜誌
    def importNews(self, site_code, isOld):
        portal = self.portal
        request = self.portal.REQUEST
        alsoProvides(request, IDisableCSRFProtection)
        try:
            # 建立DB 連線資訊定設定中文編碼utf-8
            db = MySQLdb.connect(host=self.host, port=int(self.port), user=self.user, passwd=self.passwd, db=self.db, charset=self.charset)
            sql_newsType = "SELECT * FROM `ns_type`"
            # 執行SQL statement
            cursor = db.cursor()
            cursor.execute(sql_newsType)
            old_newsType = cursor.fetchall()
            new_newsType = {}
            for item in old_newsType:
                new_newsType[item[1]] = item[2]

            sql_getNews = ''
            if isOld == 'old':
                while True:
                    for folderItem in portal['news'].getChildNodes():
                        if not folderItem.getChildNodes():
                            print 'id: %s' % folderItem.id
                            sql_getNews = "SELECT * FROM `ns_news` WHERE `NewsTypeID` = '%s' AND `CreateTime` > '2014-01-01 00:00:00' ORDER BY `CreateTime` DESC" % folderItem.id
                            break
                    break
            else:
                sql_getNews = "SELECT * FROM `ns_news` WHERE `CreateTime` > '%s' ORDER BY `ns_news`.`NewsDate` ASC" % queryTime

            if not sql_getNews:
                return
#            import pdb; pdb.set_trace()
            print DateTime()
            cursor.execute(sql_getNews)
            # 撈取多筆資料
            results = cursor.fetchall()
            # 迴圈撈取資料
            print DateTime()
            count = 0
            print 'TOTAL: %s' % len(results)
#            import pdb; pdb.set_trace()

            if isOld == 'old':
                results = results[:100]
#                import pdb; pdb.set_trace()

            for record in results:
                old_NewsId = record[1]
                old_NewsTypeID = record[5]
                if old_NewsTypeID.startswith('N'):
                    if api.content.find(context=portal['news'], id=old_NewsId):
                        continue
                elif old_NewsTypeID.startswith('M'):
                    if api.content.find(context=portal['magazine'], id=old_NewsId):
                        continue

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
                        if old_NewsTypeID.startswith('N'):
                            containerFolder = portal['news']
                        elif old_NewsTypeID.startswith('M'):
                            containerFolder = portal['magazine']
                        else:
                            continue

                        newContent = api.content.create(
                            container=containerFolder[old_NewsTypeID.lower()],
                            type='News Item',
                            id=old_NewsId,
                            title=old_Title,
                            description=old_Title,
                            oldPicturePath=old_PicturePath,
#                            oldKeywords=old_KeyWord,
                            keywords=old_KeyWord,
                            oldCreateTime=old_CreateTime,
                            freeContent=RichTextValue(old_NewsContents),
                            text=RichTextValue(old_NewsContents),
                        )
                    except:
                        continue
#                    subject = old_KeyWord.split(',')
#                    subject.append(containerFolder[old_NewsTypeID.lower()].title)
#                    newContent.setSubject(tuple(subject))
#                    api.content.transition(obj=newContent, transition='publish')

                    # import Image
                    oldImage = self.getImage(old_PicturePath)
                    if oldImage:
                        newContent.image = oldImage

                    newContent.reindexObject()

                    count += 1
                    print '%s: %s, %s' % (count, old_NewsTypeID, old_NewsId)
                    if count % 10 == 0:
                        transaction.commit()
#                    import pdb; pdb.set_trace()
#                    break
            db.close()
#            import pdb; pdb.set_trace()
        except MySQLdb.Error as e:
            print "Error %d: %s" % (e.args[0], e.args[1])


instance = ImportContents(sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
instance.getDocs(sys.argv[5], sys.argv[6], sys.argv[7])



