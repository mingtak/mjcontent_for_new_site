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
import html2text
import urllib2
import logging
import json
import pyopencc
import jieba

from naiveBayesClassifier import tokenizer
from naiveBayesClassifier.trainer import Trainer
from naiveBayesClassifier.classifier import Classifier


# howto: bin/client1 run pathtofile/import_news.py portal_name admin_id news_site_code(ex. bbc)
# mapping: sys.argv[3] is portal_name, sys.argv[4] is admin_id, sys.argv[5] is news_site_code
#          sys.argv[6] is dataType, 'xml', 'html' ...

news_site_code = {
    'bbc':'http://feeds.bbci.co.uk/zhongwen/trad/rss.xml',
}

logger = logging.getLogger('Import News')


class ImportNews:

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

        if site_code in ['liveProgram_1', 'liveProgram_2']:
            self.liveProgram(site_code, docs)
            transaction.commit()
            return

        if self.dataType == 'xml':
            soup = BeautifulSoup(docs, "xml")
        elif self.dataType == 'html':
            soup = BeautifulSoup(docs, "lxml")
        elif self.dataType == "html5":
            soup = BeautifulSoup(docs, "html5lib")
        else:
            soup = BeautifulSoup(docs, "xml")

        # To youtube_radio
#        if site_code == 'youtube_radio':
#            result = self.youtubeRadioList(soup)
#            transaction.commit()
#            return

        if site_code == 'bbc':
            result = self.getBBCNews(soup)
            transaction.commit()
            return


    def getBBCNews(self, soup):

        portal = self.portal
        request = self.portal.REQUEST
        catalog = portal.portal_catalog

        for item in soup.findAll('item'):
            link = unicode(item.link.string)

            if catalog(originalUrl=link):
                continue

            webPage = urllib2.urlopen(link)
            pageSoup = BeautifulSoup(webPage, "lxml")

#            import pdb; pdb.set_trace()
            try:
#                if site_code == 'bbc':

                # 取得html及keywords(完整列表)
                result, keywords = self.bbcNewsContent(pageSoup)
            except:continue

            title, text = result['title'], result['text']

            if len(text) < 50:
                continue

            newsCat = ''
            for key in keywords:
#                if key.startswith('n'):
                if key in ['n01', 'n07', 'n06', 'n02', 'n12', 'n16', 'n99']:
                    newsCat = key
                    break

            #取得registry
            reg = api.portal.get_registry_record('mingjing.content.browser.mjnetSetting.IMJNetSetting.catDict')

            subject = []
            for key in keywords[0:6]:
                if key != newsCat:
                    for item in reg.keys():
                        if item.startswith(key):
                            keyTitle = item.split('|||')[1]
                            break
                    subject.append(keyTitle)

#            import pdb; pdb.set_trace()
            news = api.content.create(
                type='News Item',
                id=DateTime().strftime('%Y%m%d%H%M%s'),
                title=title,
                text=RichTextValue(text),
                originalUrl=link,
                container=portal[newsCat],
            )
            news.setSubject(tuple(subject))

            portal[newsCat].moveObjectsToTop(news.id)
#            api.content.transition(obj=news, transition='publish')

            transaction.commit()
            print '%s: %s' % (title, news.absolute_url())


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

        while text.find('script'):
            text.find('script').decompose()

        for tag in text.findAll():
            if tag.has_attr('class'):
                del tag['class']
            if tag.has_attr('id'):
                del tag['id']
        if text.has_attr('class'):
            del text['class']
        if text.has_attr('id'):
            del text['id']

#        import pdb; pdb.set_trace()

        text = unicode(text)
        keywords = self.getKeywords(text)
        text += u'<p>新聞來源:BBC中文網<p>'

        return [{'title':title, 'text':text}, keywords]


    def zhsJieba(self, text):

        # 轉為簡體
        cc = pyopencc.OpenCC('zht2zhs.ini')
        text = cc.convert(text)

        #用jibea分詞
        seg_list = jieba.cut(text)
        return ' '.join(seg_list)


    def getKeywords(self, html):

        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_emphasis = True
        h.ignore_images = True
        #取得純文字
        text = h.handle(html)[:100]
#        print text
        text = self.zhsJieba(text)

        #取得registry
        reg = api.portal.get_registry_record('mingjing.content.browser.mjnetSetting.IMJNetSetting.catDict')
        trainSet = []
        for item in reg:
            key = item.split('|||')[0]
            for line in reg[item].split('\n'):
                zhsString = self.zhsJieba(line)
                trainSet.append({'category': key, 'text': zhsString})

        #用簡單貝氏分類文章
        newsTrainer = Trainer(tokenizer)
        for news in trainSet:
            newsTrainer.train(news['text'].encode('utf-8'), news['category'])
        newsClassifier = Classifier(newsTrainer.data, tokenizer)
        classification = newsClassifier.classify(text)
        print classification
#        import pdb; pdb.set_trace()
        if classification[0][1] == 0.0:
            classification.insert(0, (u'n99', 0.0))
        result = []
        for item in classification:
            result.append(item[0])
        return result


instance = ImportNews(sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
instance.getDocs(sys.argv[5])
