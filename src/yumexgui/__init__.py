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

# yum extender gui module

import sys
import gtk
import pango

from datetime import date
from optparse import OptionParser

from yumexgui.gui import Notebook, PackageCache, Notebook, PackageInfo
from guihelpers import  Controller, TextViewConsole, doGtkEvents, busyCursor, normalCursor, doLoggerSetup
from yumexgui.dialogs import Progress, TransactionConfirmation, ErrorDialog, okDialog
from yumexgui.views import YumexPackageView, YumexQueueView, YumexRepoView, YumexGroupView
from yumexbase.constants import *
from yumexbase import YumexFrontendBase, YumexBackendFatalError
import yumexbase.constants as const

# We want these lines, but don't want pylint to whine about the imports not being used
# pylint: disable-msg=W0611
import logging
from yumexbase.i18n import _, P_
# pylint: enable-msg=W0611

class YumexFrontend(YumexFrontendBase):
    '''
    Yumex Frontend  class

    This is a frontend callback class used by the backend and
    transaction to notify the frontend about changes.
    '''

    def __init__(self, backend, progress):
        ''' Setup the frontend callbacks '''
        self.logger = logging.getLogger(YUMEX_LOG)
        YumexFrontendBase.__init__(self, backend, progress)
        
    def set_state(self, state):
        ''' set the state of work '''
        pass

    def get_progress(self):
        ''' Get the current progress object '''
        return self._progress

    def set_progress(self, progress):
        ''' trigger at progress update'''
        self._progress = progress

    def confirm_transaction(self, transaction):
        ''' confirm the current transaction'''
        dialog = self.transactionConfirm
        dialog.populate(transaction)
        ok = dialog.run()
        dialog.destroy()
        return ok

    def error(self, msg, exit_pgm = False):
        ''' Write an error message to frontend '''
        self.logger.error('ERROR: %s' % msg)
        self.refresh()
        if exit_pgm:
            sys.exit(1)
            

    def warning(self, msg):
        ''' Write an warning message to frontend '''
        self.logger.warning('WARNING: %s' % msg)
        self.refresh()

    def info(self, msg):
        ''' Write an info message to frontend '''
        print msg
        self.logger.info(msg)
        self.refresh()

    def debug(self, msg):
        ''' Write an debug message to frontend '''
        if self.cmd_options.debug:
            print "DEBUG:", msg
            self.logger.debug('DEBUG: %s' % msg)
        self.refresh()

    def exception(self, msg):
        ''' handle an expection '''
        msg = msg.replace(";", "\n")
        print "exception:", msg
        sys.exit(1)

    def reset(self):
        ''' trigger a frontend reset '''
        pass

    def timeout(self, count):
        if (count > 0 and count % 600 == 0):
            self.debug('Current backend action has been running for %i min' % int(count / 600))
        self.refresh()
        
    def refresh(self):     
        progress = self.get_progress()  
        if progress:        
            if progress.is_active() and progress.is_pulse():
                progress.pulse()
        doGtkEvents()
        
class YumexHandlers(Controller):
    ''' This class contains all glade signal callbacks '''
    
    
    def __init__(self):
        # init the Controller Class to connect signals etc.
        Controller.__init__(self, BUILDER_FILE , 'main', 'yumex')
        self._last_filter = None
        self.default_repos = []
        self.current_repos = []
        self._resized = False

# Signal handlers
      
    def quit(self):
        ''' destroy Handler '''
        self.backend.debug("Quiting the program !!!")
        self.backend.reset()
        self.backend.debug("Backend reset completted")

    # Menu
        
    def on_fileQuit_activate(self, widget = None, event = None):
        self.main_quit()

    def on_editPref_activate(self, widget = None, event = None):
        okDialog(self.window, "This function has not been implemented yet")
        self.debug("Edit -> Preferences")

    def on_proNew_activate(self, widget = None, event = None):
        okDialog(self.window, "This function has not been implemented yet")
        self.debug("Profiles -> New")

    def on_proSave_activate(self, widget = None, event = None):
        okDialog(self.window, "This function has not been implemented yet")
        self.debug("Profiles -> Save")
        
    def on_helpAbout_activate(self, widget = None, event = None):
        okDialog(self.window, "This function has not been implemented yet")
        self.debug("Help -> About")

    def on_viewPackages_activate(self, widget = None, event = None):
        self.notebook.set_active("package")

    def on_viewQueue_activate(self, widget = None, event = None):
        self.notebook.set_active("queue")

    def on_viewRepo_activate(self, widget = None, event = None):
        self.notebook.set_active("repo")
        
    def on_viewOutput_activate(self, widget = None, event = None):
        self.notebook.set_active("output")
        
    # Package Page    
        
    def on_packageSearch_activate(self, widget = None, event = None):
        ''' Enter pressed in search field '''
        busyCursor(self.window)
        self.packageInfo.clear()
        filters = ['name', 'summary']
        keys = self.ui.packageSearch.get_text().split(' ')
        pkgs = self.backend.search(keys, filters)
        self.ui.packageFilterBox.hide()
        self._last_filter.set_active(True)            
        self.packages.add_packages(pkgs)
        normalCursor(self.window)
        
    def on_packageView_cursor_changed(self, widget):    
        '''  package selected in the view '''
        (model, iterator) = widget.get_selection().get_selected()
        if model != None and iterator != None:
            pkg = model.get_value(iterator, 0)
            if pkg:
                self.packageInfo.update(pkg)
                

    def on_packageClear_clicked(self, widget = None, event = None):
        self.ui.packageSearch.set_text('')
        self.ui.packageFilterBox.show()
        if self._last_filter:
            self._last_filter.clicked()
            

    def on_packageSelectAll_clicked(self, widget = None, event = None):
        self.packages.selectAll()

    def on_packageUndo_clicked(self, widget = None, event = None):
        self.packages.deselectAll()

    def on_packageFilter_changed(self, widget, active):
        if widget.get_active():
            self._last_filter = widget
            self.packageInfo.clear()
            self.ui.packageSearch.set_text('')        
            if active < 3: # Updates,Available,Installed
                self.ui.groupVBox.hide()
                if self._resized:
                    width, height = self.window.get_size()
                    self.window.resize(width - 150, height)
                    self._resized = False
                busyCursor(self.window)
                self.backend.setup()
                pkgs = self.package_cache.get_packages(PKG_FILTERS_ENUMS[active])
                action = ACTIONS[active]
                self.packages.add_packages(pkgs, progress = self.progress)
                normalCursor(self.window)
            else: # Groups
                if not self._resized:
                    width, height = self.window.get_size()
                    self.window.resize(width + 150, height)
                    self._resized = True
                self.ui.groupVBox.show_all()
                self.packages.clear()
                
    def on_groupView_cursor_changed(self, widget):
        ''' Group/Category selected in groupView '''
        (model, iterator) = widget.get_selection().get_selected()
        if model != None and iterator != None:
            desc = model.get_value(iterator, 5)
            self.groupInfo.clear()
            self.groupInfo.write(desc)
            self.groupInfo.goTop()
            isCategory = model.get_value(iterator, 4)
            if not isCategory:
                grpid = model.get_value(iterator, 2)
                pkgs = self.backend.get_group_packages(grpid, grp_filter = GROUP.all)
                self.packages.add_packages(pkgs)
            
    # Repo Page    
        
    def on_repoRefresh_clicked(self, widget = None, event = None):
        repos = self.repos.get_selected()
        self.current_repos = repos
        self.reload(repos)
        
    def on_repoUndo_clicked(self, widget = None, event = None):
        self.repos.populate(self.default_repos)

    # Queue Page    

    def on_queueOpen_clicked(self, widget = None, event = None):
        self.debug("Queue Open")
    
    def on_queueSave_clicked(self, widget = None, event = None):
        self.debug("Queue Save")
    
    def on_queueRemove_clicked(self, widget = None, event = None):
        self.queue.deleteSelected()
        
    def on_Execute_clicked(self, widget = None, event = None):
        self.notebook.set_active("output")
        self.debug("Starting pending actions processing")
        self.process_queue()
        self.debug("Ended pending actions processing")
        
    def on_progressCancel_clicked(self, widget = None, event = None):
        self.debug("Progress Cancel pressed")
                

class YumexApplication(YumexHandlers, YumexFrontend):
    """
    The Yum Extender main application class 
    """
    
    def __init__(self, backend):
        self.progress = None
        self.logger = logging.getLogger(YUMEX_LOG)
        self.debug_options = []        
        (self.cmd_options, self.cmd_args) = self.setupOptions()
        self.backend = backend(self)
        YumexHandlers.__init__(self)
        progress = Progress(self.ui, self.window)
        YumexFrontend.__init__(self, self.backend, progress)
        self.debug_options = [] # Debug options set in os.environ['YUMEX_DBG']        
        self.package_cache = PackageCache(self.backend)

    def setupOptions(self):
        parser = OptionParser()
        parser.add_option("-d", "--debug",
                        action = "store_true", dest = "debug", default = False,
                        help = "Debug mode")
        parser.add_option("", "--noplugins",
                        action = "store_false", dest = "plugins", default = True,
                        help = "Disable yum plugins")
        parser.add_option("-n", "--noauto",
                        action = "store_false", dest = "autorefresh", default = True,
                        help = "No automatic refresh af program start")
        parser.add_option("", "--debuglevel", dest = "yumdebuglevel", action = "store",
                default = 2, help = "yum debugging output level", type = 'int',
                metavar = '[level]')      
        return parser.parse_args()
    
    def run(self):
        # setup
        try:
            self.setup_gui()
            self.backend.setup()
            gtk.main()
        except YumexBackendFatalError, e:
            self.handle_error(e.err, e.msg)
            
    def handle_error(self, err, msg):        
        title = _("Fatal Error")
        if err == 'lock-error': # Cant get the yum lock
            text = _("Can't start the yum backend")
            longtext = _("Another program is locking yum")
            longtext += '\n\n'            
            longtext += _('Message from yum backend:')            
            longtext += '\n\n'            
            longtext += msg            
        else:
            text = _("Unknown Error : ") + msg
            longtext = ""
            
        # Show error dialog    
        dialog = ErrorDialog(self.ui, self.window, title, text, longtext, modal = True)
        dialog.run()
        dialog.destroy()
        self.main_quit()
                    
# shut up pylint whinning about attributes declared outside __init__
# pylint: disable-msg=W0201

    def setup_gui(self):
        # setup
        self.window.set_title("Yum Extender NextGen")
        # Calc font constants based on default font 
        const.DEFAULT_FONT = self.window.get_pango_context().get_font_description()
        const.XSMALL_FONT.set_size(const.DEFAULT_FONT.get_size() - 2 * 1024)
        const.SMALL_FONT.set_size(const.DEFAULT_FONT.get_size() - 1 * 1024)
        const.BIG_FONT.set_size(const.DEFAULT_FONT.get_size() + 4 * 1024)
        font_size = const.SMALL_FONT.get_size() / 1024
        # Setup Output console
        self.output = TextViewConsole(self.ui.outputText, font_size = font_size)
        # Setup main page notebook
        self.notebook = Notebook(self.ui.mainNotebook, self.ui.MainLeftContent)
        self.notebook.add_page("package", "Packages", self.ui.packageMain, icon = ICON_PACKAGES)
        self.notebook.add_page("queue", "Pending Action Queue", self.ui.queueMain, icon = ICON_QUEUE)
        self.notebook.add_page("repo", "Repositories", self.ui.repoMain, icon = ICON_REPOS)
        self.notebook.add_page("output", "Output", self.ui.outputMain, icon = ICON_OUTPUT)
        self.ui.groupView.hide()
        self.notebook.set_active("output")
        # setup queue view
        self.queue = YumexQueueView(self.ui.queueView)
        # setup package and package info view
        self.packages = YumexPackageView(self.ui.packageView, self.queue)
        self.packageInfo = PackageInfo(self.window, self.ui.packageInfo, 
                                       self.ui.packageInfoSelector, self, font_size = font_size)
        # setup group and group description views
        self.groups = YumexGroupView(self.ui.groupView, self.queue, self)
        self.groupInfo = TextViewConsole(self.ui.groupDesc, font_size = font_size)
        # setup repo view
        self.repos = YumexRepoView(self.ui.repoView)
        # setup transaction confirmation dialog
        self.transactionConfirm = TransactionConfirmation(self.ui, self.window)
        # setup yumex log handler
        self.log_handler = doLoggerSetup(self.output, YUMEX_LOG, logfmt = '%(asctime)s : %(message)s')
        self.window.show()
        # set up the package filters ( updates, available, installed, groups)
        self.setup_filters()
        # load packages and groups 
        if self.cmd_options.autorefresh:
            self.populate_package_cache()
            self.setup_groups()
            self.notebook.set_active("package")
        else:
            self.notebook.set_active("repo")
        # setup repository view    
        repos = self.backend.get_repositories()
        self.repos.populate(repos)
        active_repos = self.repos.get_selected()
        self.default_repos = active_repos
        self.current_repos = active_repos
        # setup default package filter (updates)
        self.ui.packageRadioUpdates.clicked()

# pylint: enable-msg=W0201


    def setup_filters(self):
        ''' Populate Package Filter radiobuttons'''
        num = 0
        for attr in ('Updates', 'Available', 'Installed', 'Groups'):
            rb = getattr(self.ui, 'packageRadio' + attr)
            rb.connect('clicked', self.on_packageFilter_changed, num) 
            num += 1
            rb.child.modify_font(SMALL_FONT)
            
    def setup_groups(self):
        progress = self.get_progress()
        self.debug("Getting Group information - BEGIN")
        progress.set_title(_("Getting Group information"))
        progress.set_header(_("Getting Group information"))
        progress.set_pulse(True)
        progress.show()
        groups = self.backend.get_groups()
        self.groups.populate(groups)
        progress.hide()
        progress.set_pulse(False)
        self.debug("Getting Group information - END")
        
    def populate_package_cache(self, repos = []):
        if not repos:
            repos = self.current_repos
        progress = self.get_progress()
        progress.set_pulse(True)
        self.debug("Getting package lists - BEGIN")
        progress.set_title(_("Getting Package Lists"))
        progress.set_header("Getting Updated Packages")
        progress.show()
        self.backend.setup(repos)
        pkgs = self.package_cache.get_packages(FILTER.updates)
        progress.set_header("Getting Available Packages")
        pkgs = self.package_cache.get_packages(FILTER.available)
        progress.set_header("Getting installed Packages")
        pkgs = self.package_cache.get_packages(FILTER.installed)
        self.debug("Getting package lists - END")
        progress.set_pulse(False)
        progress.hide()
        
    def process_queue(self):
        try:
            progress = self.get_progress()
            progress.set_pulse(True)        
            progress.set_title(_("Processing pending actions"))
            progress.set_header(_("Preparing the transaction"))
            progress.show()        
            queue = self.queue.queue
            for action in ('install', 'update', 'remove'):
                pkgs = queue.get(action[0])
                for po in pkgs:
                    self.backend.transaction.add(po, action)
            rc = self.backend.transaction.process_transaction()                    
            if rc:
                self.debug("Transaction Completed OK")
                progress.hide()        
                okDialog(self.window, _("Transaction completed successfully"))
                self.reload()
            elif rc == None: # Aborted by user
                self.warning(_("Transaction Aborted by User"))
                self.notebook.set_active("package")     # show the package page
            else: # Errors in transaction
                self.debug("Transaction Failed")
            progress.hide()        
            progress.set_pulse(False)        
        except YumexBackendFatalError, e:
            self.handle_error(e.err, e.msg)

    def reload(self, repos = []):
        ''' Reset current data and restart the backend '''
        if not repos:
            repos = self.current_repos
        self.backend.reset()                    # close the backend
        self.package_cache.reset()              # clear the package cache
        self.queue.queue.clear()                # clear the pending action queue
        self.populate_package_cache(repos = repos)           # repopulate the package cache
        self.notebook.set_active("package")     # show the package page
        self.ui.packageSearch.set_text('')      # Reset search entry
        self.ui.packageFilterBox.show()         # Show the filter selector
        self.ui.packageRadioUpdates.clicked()   # Select the updates package filter
                
