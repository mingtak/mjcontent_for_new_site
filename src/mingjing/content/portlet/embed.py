from plone.app.portlets.portlets import base
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.app.vocabularies.catalog import CatalogSource
from zope.interface import implements
from mingjing.content import _


class IEmbedHTML(IPortletDataProvider):

    text = schema.TextLine(
        title=_(u"Title"),
        required=False,
        )

    embedCode = schema.Text(
        title=_(u"Embed code"),
        required=False,
        )


class Assignment(base.Assignment):
    implements(IEmbedHTML)

    def __init__(self, text='', embedCode=None):
        self.text = text
        self.embedCode = embedCode

    @property
    def title(self):
        return _(u"EmbedHTML")


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('embed.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def render(self):
        return xhtml_compress(self._template())


class AddForm(base.AddForm):
    schema = IEmbedHTML
    label = _(u"Add EmbedHTML Portlet")
    description = _(u"This portlet rendering EmbedHTML.")

    def create(self, data):
        return Assignment(
            text=data.get('text', ''),
            embedCode=data.get('embedCode'),
            )


class EditForm(base.EditForm):
    schema = IEmbedHTML
    label = _(u"Edit EmbedHTML Portlet")
    description = _(u"This portlet rendering EmbedHTML.")

