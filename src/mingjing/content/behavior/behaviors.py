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
from plone.app.textfield import RichText
from plone.app.content.interfaces import INameFromTitle
from DateTime import DateTime
import random
from plone.directives import form


class IFreeContent(model.Schema):
    """ Add RichText for Free Content """
    freeContent = RichText(
        title=_(u"Free Content"),
        required=False,
    )


class IOriginalUrl(model.Schema):
    """ Add url field for News Original URL """

    dexterity.write_permission(originalUrl='cmf.ManagePortal')
    form.mode(originalUrl='hidden')
    originalUrl = schema.URI(
        title=_(u"Original URL"),
        required=False,
    )


class IOldFields(model.Schema):
    """ Add Old Fields """
    form.mode(oldPicturePath='hidden')
    oldPicturePath = schema.TextLine(
        title=_(u"Old Picture Path"),
        required=False,
    )

    form.mode(oldKeywords='hidden')
    oldKeywords = schema.TextLine(
        title=_(u"Old Keywords"),
        required=False,
    )

    form.mode(oldCreateTime='hidden')
    oldCreateTime = schema.Datetime(
        title=_(u"Old Create Time"),
        required=False,
    )

    form.mode(oldEbookURL='hidden')
    oldEbookURL = schema.TextLine(
        title=_(u"Old Ebook URL"),
        required=False,
    )


alsoProvides(IFreeContent, IFormFieldProvider)
alsoProvides(IOriginalUrl, IFormFieldProvider)
alsoProvides(IOldFields, IFormFieldProvider)


def context_property(name):
    def getter(self):
        return getattr(self.context, name)
    def setter(self, value):
        setattr(self.context, name, value)
    def deleter(self):
        delattr(self.context, name)
    return property(getter, setter, deleter)


class OldFields(object):
    implements(IOldFields)
    adapts(IDexterityContent)

    def __init__(self,context):
        self.context = context

    # -*- Your behavior property setters & getters here ... -*-
    oldPicturePath = context_property("oldPicturePath")
    oldKeywords = context_property("oldKeywords")
    oldCreateTime = context_property("oldCreateTime")
    oldEbookURL = context_property("oldEbookURL")


class FreeContent(object):
    implements(IFreeContent)
    adapts(IDexterityContent)

    def __init__(self,context):
        self.context = context

    # -*- Your behavior property setters & getters here ... -*-
    freeContent = context_property("freeContent")


class OriginalUrl(object):
    implements(IOriginalUrl)
    adapts(IDexterityContent)

    def __init__(self,context):
        self.context = context

    # -*- Your behavior property setters & getters here ... -*-
    originalUrl = context_property("originalUrl")


class INamedFromTimeStamp(INameFromTitle):
    """ Marker/Form interface for namedFromTimeStamp
    """


class NamedFromTimeStamp(object):
    """ Adapter for NamedFromTimeStamp
    """
    implements(INamedFromTimeStamp)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    # -*- Your behavior property setters & getters here ... -*-
    @property
    def title(self):
        timeString = '%s%s' % (DateTime().strftime("%Y%m%d%H%M"), random.randint(100000, 999999))
        return timeString
