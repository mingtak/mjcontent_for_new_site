# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from plone.z3cform import layout
from z3c.form import form
from plone.directives import form as Form
from zope import schema
from .. import _


class IMJNetSetting(Form.Schema):
    mysqlSetting = schema.TextLine(
        title=_(u"Mysql Connection Setting"),
        description=_(u"host,port,username,password,dbname,charset"),
        required=True,
    )

    oldSiteDB = schema.TextLine(
        title=_(u"Old Site Mysql Connection Setting"),
        description=_(u"host,port,username,password,dbname,charset"),
        required=True,
    )

    catDict = schema.Dict(
        title=_(u"Categories Dict"),
        key_type=schema.TextLine(title=u"Key"),
        value_type=schema.Text(title=u"Value"),
        required=False,
    )


class MJNetSettingControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = IMJNetSetting


MJNetSettingControlPanelView = layout.wrap_form(MJNetSettingControlPanelForm, ControlPanelFormWrapper)
MJNetSettingControlPanelView.label = _(u"MJNet Setting")
