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

# howto: bin/client1 run pathtofile/import_news.py portal_name admin_id news_site_code(ex. bbc)
# mapping: sys.argv[3] is portal_name, sys.argv[4] is admin_id, sys.argv[5] is news_site_code

news_site_code = {
    'bbc':'http://feeds.bbci.co.uk/zhongwen/trad/rss.xml',
}

logger = logging.getLogger('Import News')



class ImportNews:

    def __init__(self, portal, admin, news_site):
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


    def getDocs(self, site_code):
        portal = self.portal
        request = self.portal.REQUEST
        catalog = portal.portal_catalog
        alsoProvides(request, IDisableCSRFProtection)

        docs = urllib2.urlopen(self.news_site)
        if docs.getcode() == 200:
            docs = docs.read()
        else:
            logger.error('Wrong response, response code: %s' % docs.getcode())
            exit()

        soup = BeautifulSoup(docs, "xml")

        for item in soup.findAll('item'):
            link = unicode(item.link.string)

            # catalog 查看是否已存在
### TODO: url index 未建
#            import pdb; pdb.set_trace()
            if catalog({'Type':'News Item', 'originalUrl':link}):
                continue

            webPage = urllib2.urlopen(link)
            pageSoup = BeautifulSoup(webPage, "lxml")

            try:
                if site_code == 'bbc':
                    result = self.bbcNewsContent(pageSoup)
            except:continue

            title, text = result['title'], result['text']

            if len(text) < 50:
                continue

            news = api.content.create(
                type='News Item',
                title=title,
                text=RichTextValue(text),
                originalUrl=link,
                container=portal['news'],
            )

            portal['news'].moveObjectsToTop(news.id)
            api.content.transition(obj=news, transition='publish')

            transaction.commit()
            print title


    def bbcNewsContent(self, pageSoup):
        title = unicode(pageSoup.find(class_='story-body__h1').string)
        text = pageSoup.find(class_='story-body__inner')
        if text is None:
            text = pageSoup.find(class_='story-body')

        if text.find(class_='related-items'):
            text.find(class_='related-items').decompose()

        while True:
            tag = text.find(class_='js-delayed-image-load')
            if not tag:
                break

            img_tag = pageSoup.new_tag("img")
            img_tag['src'] = tag.get('data-src')
            text.find(class_='js-delayed-image-load').replace_with(img_tag)



        while text.find(class_='off-screen'):
            text.find(class_='off-screen').decompose()

        while text.find(class_='story-image-copyright'):
            text.find(class_='story-image-copyright').decompose()

        text = unicode(text)
        text += u'<p>新聞來源:BBC中文網<p>'
        return {'title':title, 'text':text}





instance = ImportNews(sys.argv[3], sys.argv[4], sys.argv[5])
instance.getDocs(sys.argv[5])
