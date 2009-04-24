#!/usr/bin/python -tt
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# (C) 2009 - Tim Lauridsen <timlau@fedoraproject.org>

# Yum Extender Constants

'''
'''

import os
import sys
import pango
import time
from enum import Enum

# We want these lines, but don't want pylint to whine about the imports not being used
# pylint: disable-msg=W0611
import logging
from yumexbase.i18n import _, P_
# pylint: enable-msg=W0611

# Constant

__yumex_version__ = "2.1.0" 

YUMEX_LOG = 'yumex.verbose'
# Package Types
PKG_TYPE = Enum('installed', 'available', 'update', 'obsolete')
# Package list filters
FILTER = Enum('all', 'installed', 'available', 'updates', 'obsoletes')
# Search filters
SEARCH = Enum('name', 'summary', 'description', 'ver', 'arch', 'repoid')
# Group Package filters
GROUP = Enum('all', 'default')
# State
STATE = Enum('none', 'init', 'download-meta', 'download-pkg', 'update', 'install', 'remove', 'cleanup')
# Actions
ACTIONS = {0 : 'u', 1: 'i', 2 : 'r'}
FILTER_ACTIONS = {str(FILTER.updates) : 'u', str(FILTER.available): 'i', str(FILTER.installed) : 'r'}

# Paths
MAIN_PATH = os.path.abspath(os.path.dirname(sys.argv[0]))
BUILDER_FILE = MAIN_PATH + '/yumex.glade'  
if MAIN_PATH == '/usr/share/yumex':    
    PIXMAPS_PATH = '/usr/share/pixmaps/yumex'
else:
    PIXMAPS_PATH = MAIN_PATH + '/../gfx'

# icons
ICON_YUMEX = PIXMAPS_PATH + "/yumex-icon.png"
ICON_PACKAGES = PIXMAPS_PATH + '/button-packages.png'
ICON_GROUPS = PIXMAPS_PATH + '/button-group.png'
ICON_QUEUE = PIXMAPS_PATH + '/button-queue.png'
ICON_OUTPUT = PIXMAPS_PATH + '/button-output.png'
ICON_REPOS = PIXMAPS_PATH + '/button-repo.png'
    
# NOTE: The package filter radio buttons in the top of the package page
PKG_FILTERS_STRINGS = (_('updates'), _('available'), _('installed'))
PKG_FILTERS_ENUMS = (FILTER.updates, FILTER.available, FILTER.installed)

REPO_HIDE = ['source', 'debuginfo']

RECENT_LIMIT = time.time() - (3600 * 24 * 14)
# Max Window size
#gdkRootWindow = gtk._root_window()
#MAX_HEIGHT = gdkRootWindow.height
#MAX_WIDHT = gdkRootWindow.width
#DEFAULT_FONT = gdkRootWindow.get_pango_context().get_font_description()

# Fonts
XSMALL_FONT = pango.FontDescription("sans 6")    
SMALL_FONT = pango.FontDescription("sans 8")    
BIG_FONT = pango.FontDescription("sans 12")    

# STRINGS

REPO_INFO_MAP = {
    'repomd'        : _("Downloading repository information"),
    'primary'       : _("Downloading Package information for the %s repository"),
    'filelists'     : _("Downloading Filelist information for the %s repository"),
    'other'         : _("Downloading Changelog information for the %s repository"),
    'group'         : _("Downloading Group information for the %s repository"),
    'updateinfo'    : _("Downloading Update information for the %s repository")
}

