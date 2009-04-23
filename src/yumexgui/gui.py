#!/usr/bin/python -tt
# -*- coding: iso-8859-1 -*-
#    Yum Exteder (yumex) - A GUI for yum
#    Copyright (C) 2008 Tim Lauridsen < tim<AT>yum-extender<DOT>org >
#
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

# Yumex gui classes & functions

'''
'''

import gtk
import gtk.glade
from datetime import date
from yumexbase.constants import *
from yumexbackend.yum_backend import YumexPackageYum
from guihelpers import TextViewBase, busyCursor, normalCursor

# We want these lines, but don't want pylint to whine about the imports not being used
# pylint: disable-msg=W0611
import logging
from yumexbase.i18n import _, P_
# pylint: enable-msg=W0611

#
# Classses
#

class PackageInfoTextView(TextViewBase):
    '''
    
    '''
    
    def __init__(self, textview, font_size = 8):
        '''
        Setup the textview
        @param textview: the gtk.TextView widget to use 
        @param font_size:
        '''
        TextViewBase.__init__(self, textview)        

        # description style
        tag = "description"
        style = gtk.TextTag(tag)
        style.set_property("foreground", "midnight blue")
        style.set_property("family", "Monospace")
        style.set_property("size_points", font_size)
        self.add_style(tag, style)
        self.default_style = tag

        # filelist style
        tag = "filelist"
        style = gtk.TextTag(tag)
        style.set_property("foreground", "DarkOrchid4")
        style.set_property("family", "Monospace")
        style.set_property("size_points", font_size)
        self.add_style(tag, style)

        # changelog style
        tag = "changelog"
        style = gtk.TextTag(tag)
        style.set_property("foreground", "midnight blue")
        style.set_property("family", "Monospace")
        style.set_property("size_points", font_size)
        self.add_style(tag, style)
        
        # changelog style
        tag = "changelog-header"
        style = gtk.TextTag(tag)
        style.set_property("foreground", "dark red")
        style.set_property("family", "Monospace")
        style.set_property("size_points", font_size)
        self.add_style(tag, style)
        
class PackageCache:
    '''
    '''
    
    def __init__(self, backend):
        '''
        
        @param backend:
        '''
        self._cache = {}
        self.backend = backend
        
    def reset(self):
        '''
        
        '''
        del self._cache
        self._cache = {}

    def get_packages(self, pkg_filter):
        '''
        
        @param pkg_filter:
        '''
        if not str(pkg_filter) in self._cache:
            pkgs = self.backend.get_packages(pkg_filter)
            pkgdict = {}
            for pkg in pkgs:
                pkgdict[str(pkg)] = pkg
            self._cache[str(pkg_filter)] = pkgdict
        return self._cache[str(pkg_filter)].values()
    
    def find(self, po):
        '''
        
        @param po:
        '''
        if po.action == 'u':
            target = self._cache[str(FILTER.updates)]
        elif po.action == 'i':
            target = self._cache[str(FILTER.available)]
        else:
            target = self._cache[str(FILTER.installed)]
        if str(po) in target:
            return(target[str(po)])
        else:   
            return YumexPackageYum(po)
    

class PageHeader(gtk.HBox):
    ''' Page header to show in top of Notebook Page'''
    
    def __init__(self, text, icon = None):
        ''' 
        setup the notebook page header
        @param text: Page Title
        @param icon: icon filename
        '''
        gtk.HBox.__init__(self)
        # Setup Label
        self.label = gtk.Label()
        markup = '<span foreground="blue" size="x-large">%s</span>' % text
        self.label.set_markup(markup)
        self.label.set_padding(10, 0)
        # Setup Icon
        self.icon = gtk.Image()
        if icon:
            self.icon.set_from_file(icon)
        else:
            self.icon.set_from_icon_name('gtk-dialog-info', 6)
        self.pack_start(self.label, expand = False)
        self.pack_end(self.icon, expand = False)
        self.show_all()

class SelectorBase:
    ''' Button selector '''
    
    def __init__(self, content):
        ''' setup the selector '''
        self.content = content
        self._buttons = {}
        self._first = None
        self._selected = None
        self.tooltip = gtk.Tooltips()
        
        
    def add_button(self, key, icon = None, stock = None, tooltip = None):
        ''' Add a new selector button '''
        if len(self._buttons) == 0:
            button = gtk.RadioButton(None)
            self._first = button
        else:
            button = gtk.RadioButton(self._first)
        button.connect("clicked", self.on_button_clicked, key)
    
        button.set_relief(gtk.RELIEF_NONE)
        button.set_mode(False)
        if stock:
            pix = gtk.image_new_from_stock(stock, gtk.ICON_SIZE_MENU)
        else: 
            pb = gtk.gdk.pixbuf_new_from_file(icon)            
            pix = gtk.Image()
            pix.set_from_pixbuf(pb)
        pix.show()
        button.add(pix)
    
        if tooltip:
            self.tooltip.set_tip(button, tooltip)
        button.show()
        self.content.pack_start(button, False)
        self._buttons[key] = button

    def set_active(self, key):
        ''' set the active selector button '''
        if key in self._buttons:
            button = self._buttons[key]
            button.clicked()
            
    def get_active(self):
        ''' get the active selector button'''
        return self._selected            
            
    def on_button_clicked(self, widget = None, key = None):
        ''' button clicked callback handler'''
        if widget.get_active(): # only work on the active button
            self._selected = key

class PackageInfo(SelectorBase):
    '''
    
    '''
    
    def __init__(self, main, console, selector, frontend, font_size = 8):
        '''
        
        @param main:
        @param console:
        @param selector:
        @param frontend:
        @param font_size:
        '''
        SelectorBase.__init__(self, selector)
        self.console = PackageInfoTextView(console, font_size = font_size)
        self.main_window = main
        self.frontend = frontend
        self.add_button('description', stock = 'gtk-about', tooltip = 'Package Description')
        self.add_button('changelog', stock = 'gtk-edit', tooltip = 'Package Changelog')
        self.add_button('filelist', stock = 'gtk-harddisk', tooltip = 'Package Filelist')
        self.pkg = None
        self._selected = 'description'

    def update(self, pkg):
        '''
        
        @param pkg:
        '''
        self.pkg = pkg
        self.set_active(self._selected)
        
    def clear(self):        
        '''
        
        '''
        self.console.clear()

    def on_button_clicked(self, widget = None, key = None):
        ''' button clicked callback handler'''
        if widget.get_active(): # only work on the active button
            self._selected = key
            self.update_console(key)
    
    def update_console(self, key):
        '''
        
        @param key:
        '''
        if self.pkg:
            busyCursor(self.main_window)
            self.console.clear()
            if key == 'description':
                self.show_description()
            elif key == 'changelog':
                self.show_changelog()
            elif key == 'filelist':
                self.show_filelist()
            self.console.goTop()
            normalCursor(self.main_window)
        
    def show_description(self):
        '''
        
        '''
        self.console.write(self.pkg.description)
        
    def show_changelog(self):
        '''
        
        '''
        changelog = self.pkg.changelog
        progress = self.frontend.get_progress()
        progress.hide()        
        for (c_date, c_ver, msg) in changelog:
            self.console.write("* %s %s" % (date.fromtimestamp(c_date).isoformat(), c_ver), "changelog-header")
            for line in msg.split('\n'):
                self.console.write("%s" % line, "changelog")
            self.console.write('\n')              

    def show_filelist(self):
        '''
        
        '''
        i = 0
        files = self.pkg.filelist
        progress = self.frontend.get_progress()
        progress.hide()        
        files.sort()
        for fn in files:
            self.console.write(fn, "filelist")
        
        
        
        
        
        
class PageSelector(SelectorBase):
    ''' Button notebook selector '''
    
    def __init__(self, content, notebook):
        ''' setup the selector '''
        SelectorBase.__init__(self, content)
        self.notebook = notebook
    def on_button_clicked(self, widget = None, key = None):
        ''' button clicked callback handler'''
        if widget.get_active(): # only work on the active button
            self.notebook.set_page(key) # set the new notebook page
            self._selected = key
            
class Notebook:
    ''' Notebook with button selector '''
    
    def __init__(self, notebook, selector):
        ''' setup the notebook and the selector '''
        self.notebook = notebook
        self.selector = PageSelector(selector, self)
        self._pages = {}

    def add_page(self, key, title, widget, icon = None, tooltip = None, header = True):
        ''' 
        Add a new page and selector button to notebook
        @param key: the page key (name) used by reference the page
        @param widget: the widget container to insert into the page
        @param icon: an optional icon file for the selector button
        @param tooltip: an optional tooltip for the selector button  
        '''
        num = len(self._pages)
        container = gtk.VBox()
        self._pages[key] = (num, container)
        if header:
            header = PageHeader(title, icon)
            container.pack_start(header, expand = False, padding = 5)
            sep = gtk.HSeparator()
            sep.show()
            container.pack_start(sep, expand = False)
        # get the content from the widget and reparent it and add it to page    
        content = gtk.VBox()
        widget.reparent(content)
        container.pack_start(content, expand = True)
        content.show()
        container.show()
        self.notebook.append_page(container)
        # Add selector button
        self.selector.add_button(key, icon, tooltip)
        
    def set_active(self, key):
        '''
        set the active page in notebook and selector
        @param key: the page key (name) used by reference the page
        '''
        self.selector.set_active(key)
        
    def set_page(self, key):
        '''
        set the current notebook page
        '''
        if key in self._pages:
            num, widget = self._pages[key]
            self.notebook.set_current_page(num)
    
