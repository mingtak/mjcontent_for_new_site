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


class ITabs(IPortletDataProvider):

    text = schema.TextLine(
        title=_(u"Text"),
        required=False,
        )

    tabs = RelationList(
        title=_(u"Tabs"),
        value_type=RelationChoice(title=_(u"Related"),
                                  source=CatalogSource(portal_type='Collection'),),
        required=True,
    )


class Assignment(base.Assignment):
    implements(ITabs)

    def __init__(self, text='', tabs=None):
        self.text = text
        self.tabs = tabs

    @property
    def title(self):
        return _(u"Tabs")


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('tabs.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def render(self):
        return xhtml_compress(self._template())


class AddForm(base.AddForm):
    schema = ITabs
    label = _(u"Add Tabs Portlet")
    description = _(u"This portlet rendering Tabs.")

    def create(self, data):
        return Assignment(
            text=data.get('text', ''),
            tabs=data.get('tabs'),
            )


class EditForm(base.EditForm):
    schema = ITabs
    label = _(u"Edit Tabs Portlet")
    description = _(u"This portlet rendering Tabs.")

