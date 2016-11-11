# -*- coding: utf-8 -*-
from mingjing.content import _
# from plone.autoform import directives
from plone.supermodel import directives
from zope import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.component import adapts
from zope.interface import alsoProvides, implements
from zope.interface import provider
from z3c.relationfield.schema import RelationList, RelationChoice
from plone.app.vocabularies.catalog import CatalogSource
from plone.dexterity.interfaces import IDexterityContent
from plone.directives import dexterity


class IOriginalUrl(model.Schema):
    """Add url field for News Original URL
    """

    dexterity.write_permission(originalUrl='cmf.ManagePortal')
    originalUrl = schema.URI(
        title=_(u"Original URL"),
        required=False,
    )


alsoProvides(IOriginalUrl, IFormFieldProvider)


def context_property(name):
    def getter(self):
        return getattr(self.context, name)
    def setter(self, value):
        setattr(self.context, name, value)
    def deleter(self):
        delattr(self.context, name)
    return property(getter, setter, deleter)


class OriginalUrl(object):
    implements(IOriginalUrl)
    adapts(IDexterityContent)

    def __init__(self,context):
        self.context = context

    # -*- Your behavior property setters & getters here ... -*-
    originalUrl = context_property("originalUrl")

