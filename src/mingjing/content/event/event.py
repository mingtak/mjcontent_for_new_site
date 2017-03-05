# -*- coding: utf-8 -*-
from plone import api
import html2text
import transaction

def updateDescription(item, event):
    if not hasattr(item, 'description'):
        return
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_emphasis = True
    h.ignore_images = True
    try:
        if getattr(item, 'freeContent'):
            item.description = h.handle(item.freeContent.raw)[0:100]
        elif getattr(item, 'text'):
            item.description = h.handle(item.text.raw)[0:100]
        else:
            return
    except:
        return
    item.reindexObject(idxs=['Description'])
    transaction.commit()


def toFolderContents(item, event):
#    parent = item.getParentNode()
    try:
        if item.Type() in ['Folder', 'Image']:
            return
        if item.Type() == 'Folder':
            item.REQUEST.response.redirect('%s/folder_contents' % item.absolute_url())
        else:
            item.REQUEST.response.redirect('%s/folder_contents' % item.getParentNode().absolute_url())
    except:pass


def userLoginToFolderContents(event):
    portal = api.portal.get()
    current = api.user.get_current()
    reporterGroup = api.group.get(groupname='reporter')
    groups = api.group.get_groups(user=current)
    if reporterGroup in groups:
        portal.REQUEST.response.redirect('%s/news/folder_contents' % portal.absolute_url())


def moveContentToTop(item, event):
    """ Moves Item to the top of its folder """
    folder = item.getParentNode()
    if not hasattr(folder, 'moveObjectsToTop'):
        return

    if item.portal_type not in ['File', 'Image']:
        try:
            folder.moveObjectsToTop(item.id)
        except:pass
