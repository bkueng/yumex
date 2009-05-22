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

'''
Yum Extender GUI main module
'''

import sys
import gtk
import pango

from datetime import date

from yumexgui.gui import Notebook, PackageCache, Notebook, PackageInfo
from yumexgui.dialogs import Progress, TransactionConfirmation, ErrorDialog, okDialog, questionDialog
from guihelpers import  Controller, TextViewConsole, doGtkEvents, busyCursor, normalCursor, doLoggerSetup
from yumexgui.views import YumexPackageView, YumexQueueView, YumexRepoView, YumexGroupView
from yumexbase.constants import *
from yumexbase import YumexFrontendBase, YumexBackendFatalError
import yumexbase.constants as const
from yumexbase.conf import YumexOptions

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

    def error(self, msg, exit_pgm=False):
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
        if self.settings.debug:
            print "DEBUG:", msg
            self.logger.debug('DEBUG: %s' % msg)
        self.refresh()

    def exception(self, msg):
        ''' handle an expection '''
        #self.progress.hide()
        print "Exception:", msg
        title = "Exception in Yum Extender"
        text = "An exception was triggered "
        longtext = msg            
        # Show error dialog    
        dialog = ErrorDialog(self.ui, self.window, title, text, longtext, modal=True)
        dialog.run()
        dialog.destroy()
        try: # try to close nicely
            self.main_quit()
        except: # exit
            sys.exit(1)

    def reset(self):
        ''' trigger a frontend reset '''
        pass

    def timeout(self, count):
        '''
        Called on backend timeout (default 0.1 sec)
        @param count: Number of calls, since start of current action
        '''
        if (count > 0 and count % 600 == 0):
            self.debug('Current backend action has been running for %i min' % int(count / 600))
        self.refresh()
        
    def refresh(self):     
        '''
        Refresh the gui and pulse the progress if enabled and in pulse mode
        '''
        progress = self.get_progress()  
        if progress:        
            if progress.is_active() and progress.is_pulse():
                progress.pulse()
        doGtkEvents()
        
class YumexHandlers(Controller):
    ''' This class contains all signal callbacks '''
    
    
    def __init__(self):
        '''
        Init the signal callback Controller 
        '''
        # init the Controller Class to connect signals etc.
        Controller.__init__(self, BUILDER_FILE , 'main', domain='yumex')
        self._last_filter = None
        self.default_repos = []
        self.current_repos = []
        self._resized = False
        self._current_active = None
        
# Signal handlers
      
    def quit(self):
        ''' destroy Handler '''
        self.backend.debug("Quiting the program !!!")
        try:
            self.backend.reset()
        except:
            pass
        self.backend.debug("Backend reset completted")

    # Menu
        
    def on_fileQuit_activate(self, widget=None, event=None):
        '''
        Menu : File -> Quit
        '''
        self.main_quit()

    def on_editPref_activate(self, widget=None, event=None):
        '''
        Menu : Edit -> Preferences
        '''
        okDialog(self.window, "This function has not been implemented yet")
        self.debug("Edit -> Preferences")

    def on_proNew_activate(self, widget=None, event=None):
        '''
        Menu : Profile -> New
        '''
        okDialog(self.window, "This function has not been implemented yet")
        self.debug("Profiles -> New")

    def on_proSave_activate(self, widget=None, event=None):
        '''
        Menu : Profile -> Save
        '''
        okDialog(self.window, "This function has not been implemented yet")
        self.debug("Profiles -> Save")
        
    def on_helpAbout_activate(self, widget=None, event=None):
        '''
        Menu : Help -> About
        '''
        self.ui.About.run()
        self.ui.About.hide()
        #okDialog(self.window, "This function has not been implemented yet")
        self.debug("Help -> About")
        
    def on_About_url(self, widget=None, event=None):
        '''
        About Dialog Url handler
        @param widget:
        '''
        # dont need to do any thing
        self.debug("About url")
    
# Options

    def on_option_nogpgcheck_toggled(self, widget=None, event=None):
        self.backend.set_option('gpgcheck',not widget.get_active(),on_repos=True)
        

    def on_viewPackages_activate(self, widget=None, event=None):
        '''
        Menu : View -> Packages
        '''
        self.notebook.set_active("package")

    def on_viewQueue_activate(self, widget=None, event=None):
        '''
        Menu : View -> Queue
        '''
        self.notebook.set_active("queue")

    def on_viewRepo_activate(self, widget=None, event=None):
        '''
        Menu : View -> Repo
        '''
        self.notebook.set_active("repo")
        
    def on_viewOutput_activate(self, widget=None, event=None):
        '''
        Menu : View -> Output
        '''
        self.notebook.set_active("output")
        
    # Package Page    
        
    def on_packageSearch_activate(self, widget=None, event=None):
        '''
        Enter pressed in the search field
        '''
        busyCursor(self.window)
        self.packageInfo.clear()
        filters = ['name', 'summary']
        keys = self.ui.packageSearch.get_text().split(' ')
        pkgs = self.backend.search(keys, filters)
        self.ui.packageFilterBox.hide()
        self._last_filter.set_active(True)            
        self.packages.add_packages(pkgs)
        normalCursor(self.window)

    def on_packageSearch_icon_press(self, widget, icon_pos, event):
        '''
        icon pressed in the search field
        '''
        if 'GTK_ENTRY_ICON_SECONDARY' in str(icon_pos):
            self.ui.packageSearch.set_text('')
            self.ui.packageFilterBox.show()
            if self._last_filter:
                self._last_filter.clicked()
            
        else:
            self.on_packageSearch_activate()
        
    def on_packageView_cursor_changed(self, widget):    
        '''
        package selected in the view 
        @param widget: the view widget
        '''
        (model, iterator) = widget.get_selection().get_selected()
        if model != None and iterator != None:
            pkg = model.get_value(iterator, 0)
            if pkg:
                if self._current_active == 0:
                    self.packageInfo.update(pkg, update=True)
                else:
                    self.packageInfo.update(pkg)

    def on_packageClear_clicked(self, widget=None, event=None):
        '''
        The clear search button 
        '''
            

    def on_packageSelectAll_clicked(self, widget=None, event=None):
        '''
        The Packages Select All button
        '''
        self.packages.selectAll()

    def on_packageUndo_clicked(self, widget=None, event=None):
        '''
        The Package Undo Button
        '''
        self.packages.deselectAll()
        self.queue.queue.remove_all_groups()
        self.groups.reset_queued()
        
    def on_packageFilter_changed(self, widget, active):
        '''
        Package filter radiobuttons
        @param widget: The radiobutton there is changed
        @param active: the button number 0 = Updates, 1 = Available, 2 = Installed, 3 = Groups
        '''
        if widget.get_active():
            self._last_filter = widget
            self._current_active = active
            self.packageInfo.clear()
            self.ui.packageSearch.set_text('')        
            if active < 3: # Updates,Available,Installed
                if active == 0: # Show only SelectAll when viewing updates
                    self.ui.packageSelectAll.show()
                else:
                    self.ui.packageSelectAll.hide()
                self.ui.groupVBox.hide()
                if self._resized:
                    width, height = self.window.get_size()
                    self.window.resize(width - 150, height)
                    self._resized = False
                busyCursor(self.window)
                self.backend.setup()
                pkgs = self.package_cache.get_packages(PKG_FILTERS_ENUMS[active])
                action = ACTIONS[active]
                self.packages.add_packages(pkgs, progress=self.progress)
                normalCursor(self.window)
                self.window.set_focus(self.ui.packageSearch) # Default focus on search entry
            else: # Groups
                if not self._resized:
                    width, height = self.window.get_size()
                    self.window.resize(width + 150, height)
                    self._resized = True
                self.ui.groupVBox.show_all()
                self.packages.clear()
                
    def on_groupView_cursor_changed(self, widget):
        '''
        Group/Category selected in groupView
        @param widget: the group view widget
        '''
        (model, iterator) = widget.get_selection().get_selected()
        if model != None and iterator != None:
            desc = model.get_value(iterator, 5)
            self.groupInfo.clear()
            self.groupInfo.write(desc)
            self.groupInfo.goTop()
            isCategory = model.get_value(iterator, 4)
            if not isCategory:
                grpid = model.get_value(iterator, 2)
                pkgs = self.backend.get_group_packages(grpid, grp_filter=GROUP.all)
                self.packages.add_packages(pkgs)
            
    # Repo Page    
        
    def on_repoRefresh_clicked(self, widget=None, event=None):
        '''
        Repo refresh button
        '''
        repos = self.repos.get_selected()
        self.current_repos = repos
        self.reload(repos)
        
    def on_repoUndo_clicked(self, widget=None, event=None):
        '''
        Repo undo button
        '''
        self.repos.populate(self.default_repos)

    # Queue Page    

    def on_queueOpen_clicked(self, widget=None, event=None):
        '''
        Queue Open Button
        '''
        self.debug("Queue Open")
    
    def on_queueSave_clicked(self, widget=None, event=None):
        '''
        Queue Save button
        '''
        self.debug("Queue Save")
    
    def on_queueRemove_clicked(self, widget=None, event=None):
        '''
        Queue Remove button
        '''
        self.queue.deleteSelected()
        
    def on_Execute_clicked(self, widget=None, event=None):
        '''
        The Queue/Packages Execute button
        '''
        self.debug("Starting pending actions processing")
        self.process_queue()
        self.debug("Ended pending actions processing")
        
    def on_progressCancel_clicked(self, widget=None, event=None):
        '''
        The Progress Dialog Cancel button
        '''
        self.debug("Progress Cancel pressed")
                

class YumexApplication(YumexHandlers, YumexFrontend):
    """
    The Yum Extender main application class 
    """
    
    def __init__(self, backend):
        '''
        Init the Yumex Application
        @param backend: The backend instance class
        '''
        self.cfg = YumexOptions()
        self.cfg.dump()
        self.progress = None
        self.logger = logging.getLogger(YUMEX_LOG)
        self.debug_options = []        
        #(self.cmd_options, self.cmd_args) = self.cfg.get_cmd_options()
        self.backend = backend(self)
        YumexHandlers.__init__(self)
        progress = Progress(self.ui, self.window)
        YumexFrontend.__init__(self, self.backend, progress)
        self.debug_options = [] # Debug options set in os.environ['YUMEX_DBG']        
        self.package_cache = PackageCache(self.backend)
    
    @property
    def settings(self):
        return self.cfg.settings
    
    def run(self):
        '''
        Run the application
        '''
        # setup
        try:
            self.setup_gui()
            self.backend.setup()
            gtk.main()
        except YumexBackendFatalError, e:
            self.handle_error(e.err, e.msg)
            
    def handle_error(self, err, msg):        
        '''
        Error message handler
        @param err: error type
        @param msg: error message
        '''
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
        dialog = ErrorDialog(self.ui, self.window, title, text, longtext, modal=True)
        dialog.run()
        dialog.destroy()
        self.main_quit()
                    
# shut up pylint whinning about attributes declared outside __init__
# pylint: disable-msg=W0201

    def setup_gui(self):
        '''
        Setup the gui
        '''
        # setup
        self.window.set_title(self.settings.branding_title)
        
        #Setup About dialog
        #gtk.about_dialog_set_url_hook(self.on_About_url) # About url handler, don't want to start firefox as root :)
        self.ui.About.set_version(const.__yumex_version__)

        # Calc font constants based on default font 
        const.DEFAULT_FONT = self.window.get_pango_context().get_font_description()
        const.XSMALL_FONT.set_size(const.DEFAULT_FONT.get_size() - 2 * 1024)
        const.SMALL_FONT.set_size(const.DEFAULT_FONT.get_size() - 1 * 1024)
        const.BIG_FONT.set_size(const.DEFAULT_FONT.get_size() + 4 * 1024)
        font_size = const.SMALL_FONT.get_size() / 1024
        # Setup Output console
        self.output = TextViewConsole(self.ui.outputText, font_size=font_size)
        # Setup main page notebook
        self.notebook = Notebook(self.ui.mainNotebook, self.ui.MainLeftContent)
        self.notebook.add_page("package", "Packages", self.ui.packageMain, icon=ICON_PACKAGES)
        self.notebook.add_page("queue", "Pending Action Queue", self.ui.queueMain, icon=ICON_QUEUE)
        if not self.settings.disable_repo_page:
            self.notebook.add_page("repo", "Repositories", self.ui.repoMain, icon=ICON_REPOS)
        self.notebook.add_page("output", "Output", self.ui.outputMain, icon=ICON_OUTPUT)
        self.ui.groupView.hide()
        self.notebook.set_active("output")
        # setup queue view
        self.queue = YumexQueueView(self.ui.queueView)
        # setup package and package info view
        self.packages = YumexPackageView(self.ui.packageView, self.queue)
        self.packageInfo = PackageInfo(self.window, self.ui.packageInfo,
                                       self.ui.packageInfoSelector, self, font_size=font_size)
        # setup group and group description views
        self.groups = YumexGroupView(self.ui.groupView, self.queue, self)
        self.groupInfo = TextViewConsole(self.ui.groupDesc, font_size=font_size)
        # setup repo view
        self.repos = YumexRepoView(self.ui.repoView)
        # setup transaction confirmation dialog
        self.transactionConfirm = TransactionConfirmation(self.ui, self.window)
        # setup yumex log handler
        self.log_handler = doLoggerSetup(self.output, YUMEX_LOG, logfmt='%(asctime)s : %(message)s')
        self.window.show()
        # set up the package filters ( updates, available, installed, groups)
        self.setup_filters()
        # load packages and groups 
        # We cant disable both repo page and auto refresh
        if self.settings.autorefresh or self.settings.disable_repo_page: 
            self.populate_package_cache()
            self.setup_groups()
            self.notebook.set_active("package")
        else:
            self.backend.setup(repos=self.current_repos)
            self.notebook.set_active("repo")
        # setup repository view    
        repos = self.backend.get_repositories()
        self.repos.populate(repos)
        self.default_repos = repos
        active_repos = self.repos.get_selected()
        self.current_repos = active_repos
        # setup default package filter (updates)
        self.ui.packageRadioUpdates.clicked()


# pylint: enable-msg=W0201


    def setup_filters(self, filters=None):
        ''' 
        Populate Package Filter radiobuttons
        '''
        num = 0
        if not filters:
            filters = ('Updates', 'Available', 'Installed', 'Groups')
        for attr in filters:
            rb = getattr(self.ui, 'packageRadio' + attr)
            rb.connect('clicked', self.on_packageFilter_changed, num) 
            num += 1
            rb.child.modify_font(SMALL_FONT)
            
    def setup_groups(self):
        '''
        Get Group information and populate the group view
        '''
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
        
    def populate_package_cache(self, repos=None):
        '''
        Get the packagelists and put them in the package cache.
        @param repos: a list of enabled repositories to use, None = use the current ones
        '''
        if not repos:
            repos = self.current_repos
        progress = self.get_progress()
        progress.set_pulse(True)
        self.debug("Getting package lists - BEGIN")
        progress.set_title(_("Getting Package Lists"))
        progress.set_header(_("Getting Updated Packages"))
        progress.show()
        self.backend.setup(repos)
        pkgs = self.package_cache.get_packages(FILTER.updates)
        progress.set_header(_("Getting Available Packages"))
        pkgs = self.package_cache.get_packages(FILTER.available)
        progress.set_header(_("Getting installed Packages"))
        pkgs = self.package_cache.get_packages(FILTER.installed)
        self.debug("Getting package lists - END")
        progress.set_pulse(False)
        progress.hide()
        
    def process_queue(self):
        '''
        Process the pending actions in the queue
        '''
        try:
            queue = self.queue.queue
            if queue.total() == 0:
                okDialog(self.window,_("The pending action queue is empty")) 
                return        
            self.notebook.set_active("output")
            progress = self.get_progress()
            progress.set_pulse(True)        
            progress.set_title(_("Processing pending actions"))
            progress.set_header(_("Preparing the transaction"))
            progress.show_tasks()
            progress.show()        
            for action in ('install', 'update', 'remove'):
                pkgs = queue.get(action[0])
                for po in pkgs:
                    self.backend.transaction.add(po, action)
            rc = self.backend.transaction.process_transaction()   
            print "transaction result", rc
            progress.hide_tasks()
            progress.hide()        
            if rc: # Transaction ok
                self.info("Transaction completed successfully")
                progress.hide()        
                msg = _("Transaction completed successfully")
                msg += _("\n\nDo you want to exit Yum Extender")
                rc = questionDialog(self.window, msg) # Ask if the user want to Quit
                if rc:
                    self.main_quit() # Quit Yum Extender
                self.reload()
            elif rc == None: # Aborted by user
                self.warning(_("Transaction Aborted by User"))
                self.notebook.set_active("package")     # show the package page
            else:
                msg = _("Transaction completed with errors,\n check output page for details")
                rc = okDialog(self.window,msg)
                
            progress.set_pulse(False)        
        except YumexBackendFatalError, e:
            self.handle_error(e.err, e.msg)

    def _get_options(self):
        '''
        Store the session based options in the Options menu
        '''
        options = []
        options.append( (self.ui.option_nogpgcheck,self.ui.option_nogpgcheck.get_active()) )
        return options
    
    def _set_options(self,options):
        '''
        Reset the session based options in the Options menu
        '''
        for (option,state) in options:
            option.set_active(state)

    def reload(self, repos=None):
        '''
        Reset current data and restart the backend 
        @param repos: a list of enabled repositories to use, None = use the current ones
        '''
        if not repos:
            repos = self.current_repos
        options = self._get_options()
        self.backend.reset()                    # close the backend
        self.package_cache.reset()              # clear the package cache
        self.queue.queue.clear()                # clear the pending action queue
        self.queue.refresh()                    # clear the pending action queue
        self.populate_package_cache(repos=repos)           # repopulate the package cache
        self.notebook.set_active("package")     # show the package page
        self.ui.packageSearch.set_text('')      # Reset search entry
        self.ui.packageFilterBox.show()         # Show the filter selector
        self._set_options(options)
        self.ui.packageRadioUpdates.clicked()   # Select the updates package filter
                
