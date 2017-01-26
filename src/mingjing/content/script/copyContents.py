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
import random
#import html2text
import urllib2
import logging

# howto: bin/client1 run pathtofile/import_news.py portal_name admin_id news_site_code(ex. bbc)
# mapping: sys.argv[3] is portal_name, sys.argv[4] is admin_id, sys.argv[5] is news_site_code


logger = logging.getLogger('Import News')



class AddKeyWords:

    def __init__(self, portal, admin):
        root = makerequest.makerequest(app)
        self.portal = getattr(root, portal, None)

        admin = root.acl_users.getUserById(admin)
        admin = admin.__of__(self.portal.acl_users)
        newSecurityManager(None, admin)
        setHooks()
        setSite(self.portal)
        self.portal.setupCurrentSkin(self.portal.REQUEST)


    def copyContents(self, fName):
        portal = self.portal
        request = self.portal.REQUEST
        catalog = portal.portal_catalog
        alsoProvides(request, IDisableCSRFProtection)

        templateFolder = portal['news']['1']
        folder = portal[fName]


        subfolder_brain = api.content.find(context=folder, Type="Folder")
        for item in subfolder_brain:
            sFolder = item.getObject()
            if sFolder.getChildNodes():
                continue

            for news in list(templateFolder.getChildNodes())[0:20]:
                api.content.copy(source=news, target=sFolder)

            transaction.commit()
            print item.getURL()



instance = AddKeyWords(sys.argv[3], sys.argv[4])
instance.copyContents(sys.argv[5])
