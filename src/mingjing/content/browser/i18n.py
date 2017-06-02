# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from Products.CMFPlone.interfaces import ILanguage
from plone.app.multilingual.interfaces import ITranslationManager
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
import logging

logger = logging.getLogger('mingjing.content')


class RegTrans(BrowserView):

    def __call__(self):
        portal = api.portal.get()
        request = self.request
        alsoProvides(request, IDisableCSRFProtection)

        id = request.form.get('id')
#        import pdb; pdb.set_trace()
        if not id:
            return
        obj_t = api.content.find(context=portal['zh-tw'], id=id)
        obj_s = api.content.find(context=portal['zh-cn'], id=id)
        if not (obj_s and obj_s):
            return
#        import pdb; pdb.set_trace()
        ILanguage(obj_t[0].getObject()).set_language('zh-tw')
        ILanguage(obj_s[0].getObject()).set_language('zh-cn')
        ITranslationManager(obj_t[0].getObject()).register_translation('zh-cn', obj_s[0].getObject())

        return

