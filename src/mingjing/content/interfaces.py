# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from mingjing.content import _
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IMingjingContentLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


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
