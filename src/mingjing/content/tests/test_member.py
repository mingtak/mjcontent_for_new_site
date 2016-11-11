# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_ID
from zope.component import queryUtility
from zope.component import createObject
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone import api

from mingjing.content.testing import MINGJING_CONTENT_INTEGRATION_TESTING  # noqa
from mingjing.content.interfaces import IMember

import unittest2 as unittest


class MemberIntegrationTest(unittest.TestCase):

    layer = MINGJING_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='Member')
        schema = fti.lookupSchema()
        self.assertEqual(IMember, schema)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='Member')
        self.assertTrue(fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='Member')
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(IMember.providedBy(obj))

    def test_adding(self):
        self.portal.invokeFactory('Member', 'Member')
        self.assertTrue(
            IMember.providedBy(self.portal['Member'])
        )
