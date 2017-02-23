# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from mingjing.content import _
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.app.vocabularies.catalog import CatalogSource
#from plone.supermodel import model
from plone.directives import form
from DateTime import DateTime

date_range = {
    'query': (DateTime()-1, DateTime()), 
    'range': 'min:max',
}


class IMingjingContentLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IBlog(Interface):
    """  """


class IEbook(Interface):
    """  """


class IYoutube(Interface):
    """  """

    youtubeURL = schema.URI(
        title=_(u"Youtube URL"),
        required=True,
    )


class IMember(Interface):
    """  """


class ICover(Interface):
    """  """

    mainSliderNews = schema.Text(
        title=_(u"Main Slider News"),
        description=_(u"Please input news id, per line one id, sorted on modified, max 10 news."),
        required=False,
    )

    todayNews = schema.Text(
        title=_(u"Today news"),
        description=_(u"Please input news id, per line one id, sorted on modified, max 8 news."),
        required=False,
    )

    tabsName = schema.Text(
        title=_(u"Tabs Name"),
        description=_(u"Please input tabs name, per line 5 tabs, Separated by commas, max 3 lines."),
        required=False,
    )

    ebooks = schema.Text(
        title=_(u"Ebooks Introduction"),
        description=_(u"Please input books id, per line 1 id, In order is Newest, Hotest and eBook."),
        required=False,
    )

    rankingNews = schema.Text(
        title=_(u"Ranking News"),
        description=_(u"Please input ranking news id, per line one id, sorted on modified, max 6 news."),
        required=False,
    )

    form.mode(radioList='hidden')
    radioList = schema.Text(
        title=_(u"Radio List"),
        description=_(u"Don't edit this, auto renew."),
        required=False,
    )

    form.mode(liveProgram_1='hidden')
    liveProgram_1 = schema.Text(
        title=_(u"Live Program 1"),
        description=_(u"Live Program 1"),
        required=False,
    )

    form.mode(liveProgram_2='hidden')
    liveProgram_2 = schema.Text(
        title=_(u"Live Program 2"),
        description=_(u"Live Program 2"),
        required=False,
    )

