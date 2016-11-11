# -*- coding: utf-8 -*-
from plone.indexer.decorator import indexer
from zope.interface import Interface
from Products.CMFPlone.utils import safe_unicode

from plone.app.contenttypes.interfaces import INewsItem


@indexer(INewsItem)
def originalUrl_indexer(obj):
    return obj.originalUrl
