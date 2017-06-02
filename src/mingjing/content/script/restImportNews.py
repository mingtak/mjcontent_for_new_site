# -*- coding: utf-8 -*-
import sys
import csv
from bs4 import BeautifulSoup
import html2text
import urllib
import urllib2
import requests
import json
import pyopencc
from datetime import datetime

# 例: python restImportNews.py username password siteURL news_site_code

news_site_code = {
#    'bbc': ('http://feeds.bbci.co.uk/zhongwen/trad/rss.xml', 'xml'),
    'cna-f': ('http://feeds.feedburner.com/rsscna/finance?format=xml', 'xml'),
    'cna-it': ('http://feeds.feedburner.com/rsscna/technology?format=xml', 'xml'),
    'cna-life': ('http://feeds.feedburner.com/rsscna/lifehealth?format=xml', 'xml'),
    'cna-cn': ('http://feeds.feedburner.com/rsscna/mainland?format=xml', 'xml'),
    'cna-sp': ('http://feeds.feedburner.com/rsscna/sport?format=xml', 'xml'),
    'dw-it': ('http://partner.dw.com/rdf/rss-chi-sci', 'xml'),
    'dw-f': ('http://partner.dw.com/rdf/rss-chi-eco', 'xml'),
    'dw-life': ('http://partner.dw.com/rdf/rss-chi-cul', 'xml'),
    'dw-sp': ('http://partner.dw.com/rdf/rss-chi-bl', 'xml'),
    'dw-inter': ('http://partner.dw.com/rdf/rss-chi-all', 'xml'),
    'rfi-asia-inter': ('http://cn.rfi.fr/%E4%BA%9A%E6%B4%B2/rss', 'xml'),
    'rfi-cn': ('http://cn.rfi.fr/%E4%B8%AD%E5%9B%BD/rss', 'xml'),
    'rfi-3land-cn': ('http://cn.rfi.fr/%E6%B8%AF%E6%BE%B3%E5%8F%B0/rss', 'xml'), #港澳台
    'rfi-am-inter': ('http://cn.rfi.fr/%E7%BE%8E%E6%B4%B2/rss', 'xml'),
    'rfi-eu-inter': ('http://cn.rfi.fr/%E6%AC%A7%E6%B4%B2/rss', 'xml'),
    'rfi-life': ('http://cn.rfi.fr/%E7%A7%91%E6%8A%80%E4%B8%8E%E6%96%87%E5%8C%96/rss', 'xml'),
    'rfi-eco-life': ('http://trad.cn.rfi.fr/%E7%94%9F%E6%85%8B/rss', 'xml'),
    'rfi-f': ('http://trad.cn.rfi.fr/%E7%B6%93%E8%B2%BF/rss', 'xml'),
    'rfi-inter': ('http://trad.cn.rfi.fr/%E5%9C%8B%E9%9A%9B/rss', 'xml'),
    'rfi-ME-inter': ('http://trad.cn.rfi.fr/%E4%B8%AD%E6%9D%B1/rss', 'xml'),
    'rfi-af-inter': ('http://trad.cn.rfi.fr/%E9%9D%9E%E6%B4%B2/rss', 'xml'),


#    'reuters-f': ('http://cn.reuters.com/rssFeed/chinaNews/', 'xml'),
}

username = sys.argv[1]
paswd = sys.argv[2]
siteURL =sys.argv[3]
siteCode = sys.argv[4]
newsSiteURL, newsSiteType = news_site_code[siteCode]


class ImportNews:

    def getDocs(self, url):
        docs = urllib2.urlopen(url)
        if docs.getcode() == 200:
            docs = docs.read()
        else:
            print 'Wrong response, response code: %s' % docs.getcode()
            docs = None
        return docs


    def transZhUrl(self, link):
        # 先只處理 dw, rfi
        if 'dw.com' in link:
            linkText = link.split('zh/')[-1].split('/a')[0]
            transText = urllib2.quote(linkText.encode('utf-8'))
        elif 'rfi.fr' in link:
            linkText = link.split('.fr/')[-1]
            transText = urllib2.quote(linkText.encode('utf-8'))
        return link.replace(linkText, transText)


    def getHtml2Text(self, html):
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_emphasis = True
        h.ignore_images = True
        #取得純文字
        text = h.handle(html)
        return text


    def cutAttrs(self, soup):
        # drop attrs and strip a tag
        while soup.find('script'):
            soup.find('script').decompose()
        while soup.find('a'):
            soup.a.unwrap()

        for tag in soup.find_all():
            for key in tag.attrs.keys():
                if key not in ['href', 'src']:
                    del tag[key]
        for key in soup.attrs.keys():
            if key not in ['href', 'src']:
                del soup[key]
        return soup


    def rfiNewsContent(self, pageSoup):
        title = unicode(pageSoup.find('h1', attrs={'itemprop':'name'}).string)
        text = pageSoup.find('article', attrs={'class':'article-page'})
        try:
            items = text.find_all('div', attrs={'class':'soc-connect clearfix'})
            for item in items:
                item.decompose()
        except:pass
        try:
            items = text.find_all('small')
            for item in items:
                item.decompose()
        except:pass
        try:
            text.find('header').decompose()
        except:pass
        try:
            text.find('div', attrs={'class':'article-pays'}).decompose()
        except:pass
        try:
            text.find('div', attrs={'class':'actions'}).decompose()
        except:pass

        text = self.cutAttrs(text)

        try:
            imgs = text.find_all('img')
            oldPicturePath = ''
            for img in imgs:
                if img['src'].startswith('http'):
                    oldPicturePath = img['src']
                    break
        except:
            oldPicturePath = ''
        print oldPicturePath
        text = unicode(text)
        text += u'<p>新聞來源:法國國際廣播電台(RFI)<p>'

        return [{'title':title, 'text':text}, oldPicturePath]


    def dwNewsContent(self, pageSoup):
        title = unicode(pageSoup.find('title').string).split('|')[0].strip()
        text = pageSoup.find(class_='longText')
#        try:
        try:
            if text.find('div', attrs={'role': 'tablist'}):
                text.find('div', attrs={'role': 'tablist'}).decompose()
        except:
            print 'error 202'

        try:
            for item in text.find_all('img'):
                if not item['src'].startswith('http'):
                    item['src'] = 'http://www.dw.com%s' % item['src']
            for item in text.find_all('em'):
                item.decompose()
        except:
            print '嚴重錯誤！'
            pass

        text = self.cutAttrs(text)

        try:
            imgs = text.find_all('img')
            oldPicturePath = ''
            for img in imgs:
                if img['src'].startswith('http'):
                    oldPicturePath = img['src']
                    break
        except:
            oldPicturePath = ''
        text = unicode(text)
        text += u'<p>新聞來源:德國之聲<p>'

        return [{'title':title, 'text':text}, oldPicturePath]


    def ncaNewsContent(self, pageSoup):
        title = unicode(pageSoup.find('title').string).split('|')[0].strip()
        text = pageSoup.find(class_='article_box')

        text = self.cutAttrs(text)

        try:
            imgs = text.find_all('img')
            oldPicturePath = ''
            for img in imgs:
                if img['src'].startswith('http'):
                    oldPicturePath = img['src']
                    break
        except:
            oldPicturePath = ''
        print oldPicturePath
        text = unicode(text)
        text += u'<p>新聞來源:中央通訊社<p>'

        return [{'title':title, 'text':text}, oldPicturePath]


    def importNews(self):
        if self.newsList is None:
            return

        listSoup = BeautifulSoup(self.newsList, newsSiteType)

        for item in listSoup.findAll('item'):
            link = unicode(item.link.string)

            # 中文網址預處理
            if siteCode.startswith('dw-') or siteCode.startswith('rfi-'):
                link = self.transZhUrl(link)

            link = str(link)

            query = requests.get(
                '%s/@search?originalUrl=%s' % (siteURL, urllib.quote(link)),
                headers={'Accept': 'application/json'},
                auth=(username, paswd),
            )
            print 'items_total: %s' % query.json().get('items_total')
            if query.json().get('items_total') > 1:
                continue

            webPage = self.getDocs(link)
            if webPage is None:
                continue
            pageSoup = BeautifulSoup(webPage, "lxml")

            try:
                # 取得html及keywords(完整列表)
                if siteCode.startswith('dw-'):
                    result, oldPicturePath = self.dwNewsContent(pageSoup)
                elif siteCode.startswith('rfi-'):
                    result, oldPicturePath = self.rfiNewsContent(pageSoup)
                elif siteCode.startswith('cna-'):
                    result, oldPicturePath = self.ncaNewsContent(pageSoup)

                title, text = result['title'], result['text']

                if len(text) < 50:
                    continue

                targetURL_TW = '%s/zh-tw/%s' % (siteURL, self.folder)
                targetURL_CN = '%s/zh-cn/%s' % (siteURL, self.folder)
                newsId = datetime.now().strftime('%Y%m%d%H%M%S')
                m2s = pyopencc.OpenCC('mix2zhs.ini')
                m2t = pyopencc.OpenCC('mix2zht.ini')
                title_t = m2t.convert(title)
                title_s = m2s.convert(title)
                text_t = m2t.convert(text)
                text_s = m2s.convert(text)
                self.addNews(targetURL_TW, newsId, title_t, text_t, link, oldPicturePath)
                self.addNews(targetURL_CN, newsId, title_s, text_s, link, oldPicturePath)
#                import pdb; pdb.set_trace()
                urllib.urlopen('http://%s:%s@%s/reg_trans?id=%s' % (username, paswd, siteURL.replace('http://', ''), newsId))

            except:
                print 'line 227'
                continue


    def addNews(self, targetURL, newsId, title, text, link, oldPicturePath):
            print '%s: %s' % (newsId, str(link))
            requests.post(
                targetURL,
                headers={'Accept': 'application/json'},
                json={'@type': 'News Item',
                    'id': newsId,
                    'title': unicode(title),
                    'description': '%s...' % self.getHtml2Text(text)[:100],
                    'text':{
                        'data': unicode(text),
                        'content-type': 'text/html',
                        'encoding': 'utf-8'
                    },
                    'originalUrl': str(link),
                    'oldPicturePath': oldPicturePath,
                },
                auth=(username, paswd)
            )


    def __init__(self):
        self.newsList = self.getDocs(newsSiteURL)
        # 01:國際 02:中國 03:財經 04:萬象
        if siteCode.endswith('-f'):
            self.folder = '03'
        elif siteCode.endswith('-it'):
            self.folder = '04'
        elif siteCode.endswith('-life'):
            self.folder = '04'
        elif siteCode.endswith('-cn'):
            self.folder = '02'
        elif siteCode.endswith('-sp'):
            self.folder = '04'
        elif siteCode.endswith('-inter'):
            self.folder = '01'


instance = ImportNews()
instance.importNews()
