# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from mingjing.content.testing import MINGJING_CONTENT_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that mingjing.content is properly installed."""

    layer = MINGJING_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if mingjing.content is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'mingjing.content'))

    def test_browserlayer(self):
        """Test that IMingjingContentLayer is registered."""
        from mingjing.content.interfaces import (
            IMingjingContentLayer)
        from plone.browserlayer import utils
        self.assertIn(IMingjingContentLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = MINGJING_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['mingjing.content'])

    def test_product_uninstalled(self):
        """Test if mingjing.content is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'mingjing.content'))

    def test_browserlayer_removed(self):
        """Test that IMingjingContentLayer is removed."""
        from mingjing.content.interfaces import IMingjingContentLayer
        from plone.browserlayer import utils
        self.assertNotIn(IMingjingContentLayer, utils.registered_layers())
