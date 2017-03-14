# -*- coding: utf-8 -*-
from plone.indexer.decorator import indexer
from zope.interface import Interface
from Products.CMFPlone.utils import safe_unicode

from plone.app.contenttypes.interfaces import INewsItem


@indexer(INewsItem)
def originalUrl_indexer(obj):
    return obj.originalUrl


@indexer(Interface)
def featured_indexer(obj):
    if hasattr(obj, 'featured'):
        return obj.featured


@indexer(Interface)
def headWeight_indexer(obj):
    if hasattr(obj, 'headWeight'):
        return obj.headWeight


@indexer(Interface)
def keywords_indexer(obj):
    if hasattr(obj, 'keywords'):
        keywords = []
        for item in obj.keywords.split(','):
            keywords.append(safe_unicode(item))
        return keywords

