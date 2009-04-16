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
import logging

from datetime import date
from optparse import OptionParser

from yumexgui.gui import Notebook, PackageCache, Notebook, PackageInfo
from guihelpers import  Controller, TextViewConsole, doGtkEvents, busyCursor, normalCursor, doLoggerSetup
from yumexgui.dialogs import Progress, TransactionConfirmation, ErrorDialog
from yumexgui.views import YumexPackageView,YumexQueueView,YumexRepoView
from yumexbase import *
from yumexbase.i18n import _, P_


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

    def set_progress(self,progress):
        ''' trigger at progress update'''
        self._progress = progress

    def confirm_transaction(self, transaction):
        ''' confirm the current transaction'''
        dialog = TransactionConfirmation(self.ui,self.window)
        dialog.populate(transaction)
        ok = dialog.run()
        dialog.destroy()
        return ok

    def error(self, msg, exit=False):
        ''' Write an error message to frontend '''
        self.logger.error('ERROR: %s' % msg)
        self.refresh()
        if exit:
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
        print "DEBUG:",msg
        self.logger.debug('DEBUG: %s' % msg)
        self.refresh()

    def exception(self, msg):
        ''' handle an expection '''
        msg = msg.replace(";","\n")
        print "exception:",msg
        sys.exit(1)

    def reset(self):
        ''' trigger a frontend reset '''
        pass

    def timeout(self,count):
        if (count > 0 and count % 600 == 0):
            self.warning('Something is rotten command has been running for %i min' % int(count/600))
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
        self.package_cache = PackageCache(self.backend)
        self._last_filter = None
        
# helpers
    def setup_gui(self):
        # setup
        self.window.set_title("Yum Extender NextGen")
        self.output = TextViewConsole(self.ui.outputText)
        self.notebook = Notebook(self.ui.mainNotebook,self.ui.MainLeftContent)
        self.notebook.add_page("package","Packages",self.ui.packageMain, icon=ICON_PACKAGES)
        self.notebook.add_page("group","Groups",self.ui.groupMain, icon=ICON_GROUPS)
        self.notebook.add_page("queue","Pending Action Queue",self.ui.queueMain, icon=ICON_QUEUE)
        self.notebook.add_page("repo","Repositories",self.ui.repoMain, icon=ICON_REPOS)
        self.notebook.add_page("output","Output",self.ui.outputMain, icon=ICON_OUTPUT)
        self.notebook.set_active("output")
        self.queue = YumexQueueView(self.ui.queueView)
        self.packages = YumexPackageView(self.ui.packageView,self.queue)
        self.packageInfo = PackageInfo(self.window,self.ui.packageInfo,self.ui.packageInfoSelector)
        self.repos = YumexRepoView(self.ui.repoView)
        self.log_handler = doLoggerSetup(self.output,YUMEX_LOG)
        self.window.show()
        self.setup_filters()
        self.populate_package_cache()
        self.notebook.set_active("package")
        self.setup_repositories()
        # setup default package filter (updates)
        self.ui.packageRadioUpdates.clicked()

    def setup_filters(self):
        ''' Populate Package Filter radiobuttons'''
        num = 0
        for attr in ('Updates','Available','Installed'):
            rb = getattr(self.ui,'packageRadio'+attr)
            rb.connect('clicked',self.on_packageFilter_changed,num) 
            num += 1
            rb.child.modify_font(SMALL_FONT)
            
    def setup_repositories(self):
        repos = self.backend.get_repositories()
        self.repos.populate(repos)
                
    def populate_package_cache(self):
        self.backend.setup()
        progress = self.get_progress()
        progress.set_pulse(True)
        progress.show()
        progress.set_title(_("Getting Package Lists"))
        progress.set_header("Getting Updated Packages")
        pkgs = self.package_cache.get_packages(FILTER.updates)
        progress.set_header("Getting Available Packages")
        pkgs = self.package_cache.get_packages(FILTER.available)
        progress.set_header("Getting installed Packages")
        pkgs = self.package_cache.get_packages(FILTER.installed)
        progress.set_pulse(False)
        progress.hide()

        
        

# Signal handlers
      
    def quit(self, widget=None, event=None ):
        ''' destroy Handler '''
        self.backend.debug("Quiting the program !!!")
        self.backend.reset()
        self.backend.debug("Backend reset completted")

    # Menu
        
    def on_fileQuit_activate(self, widget=None, event=None ):
        self.main_quit()

    def on_editPref_activate(self, widget=None, event=None ):
        self.debug("Edit -> Preferences")

    def on_proNew_activate(self, widget=None, event=None ):
        self.debug("Profiles -> New")

    def on_proSave_activate(self, widget=None, event=None ):
        self.debug("Profiles -> Save")
        
    def on_helpAbout_activate(self, widget=None, event=None ):
        self.debug("Help -> About")

    # Package Page    
        
    def on_packageSearch_activate(self, widget=None, event=None ):
        ''' Enter pressed in search field '''
        busyCursor(self.window)
        self.packageInfo.clear()
        filters = ['name','summary']
        keys = self.ui.packageSearch.get_text().split(' ')
        pkgs = self.backend.search(keys,filters)
        self.ui.packageFilterBox.hide()
        self._last_filter.set_active(True)            
        self.packages.add_packages(pkgs)
        normalCursor(self.window)
        
    def on_packageView_cursor_changed(self,widget):    
        '''  package selected in the view '''
        ( model, iterator ) = widget.get_selection().get_selected()
        if model != None and iterator != None:
            pkg = model.get_value( iterator, 0 )
            if pkg:
                self.packageInfo.update(pkg)

    def on_packageClear_clicked(self, widget=None, event=None ):
        self.ui.packageSearch.set_text('')
        self.ui.packageFilterBox.show()
        if self._last_filter:
            self._last_filter.clicked()
            

    def on_packageSelectAll_clicked(self, widget=None, event=None ):
        self.packages.selectAll()

    def on_packageUndo_clicked(self, widget=None, event=None ):
        self.packages.deselectAll()

    def on_packageFilter_changed(self, widget, active ):
        if widget.get_active():
            self._last_filter = widget
            self.packageInfo.clear()
            busyCursor(self.window)
            self.ui.packageSearch.set_text('')        
            self.backend.setup()
            pkgs = self.package_cache.get_packages(PKG_FILTERS_ENUMS[active])
            action = ACTIONS[active]
            self.packages.add_packages(pkgs,progress = self.progress)
            normalCursor(self.window)
            
    # Repo Page    
        
    def on_repoRefresh_clicked(self, widget=None, event=None ):
        self.debug("Repo Refresh")
        
    def on_repoUndo_clicked(self, widget=None, event=None ):
        self.debug("Repo Undo")

    # Queue Page    

    def on_queueOpen_clicked(self, widget=None, event=None ):
        self.debug("Queue Open")
    
    def on_queueSave_clicked(self, widget=None, event=None ):
        self.debug("Queue Save")
    
    def on_queueRemove_clicked(self, widget=None, event=None ):
        self.debug("Queue Remove")

    def on_Execute_clicked(self, widget=None, event=None ):
        self.notebook.set_active("output")
        self.debug("Starting pending actions processing")
        self.process_queue()
        self.debug("Ended pending actions processing")
        
    def on_progressCancel_clicked(self, widget=None, event=None ):
        self.debug("Progress Cancel : "+event)
                

class YumexApplication(YumexHandlers, YumexFrontend):
    """
    The Yum Extender main application class 
    """
    
    def __init__(self,backend):
        self.logger = logging.getLogger(YUMEX_LOG)
        (self.cmd_options, self.cmd_args) = self.setupOptions()
        self.backend = backend(self)
        YumexHandlers.__init__(self)
        progress = Progress(self.ui,self.window)
        self.setup_backend()
        YumexFrontend.__init__(self, self.backend, progress)


    def setupOptions(self):
        parser = OptionParser()
        parser.add_option( "-d", "--debug", 
                        action="store_true", dest="debug", default=False, 
                        help="Debug mode" )
        parser.add_option( "", "--noplugins", 
                        action="store_false", dest="plugins", default=True, 
                        help="Disable yum plugins" )
        return parser.parse_args()
    
    def setup_backend(self):
        #TODO: Add some reel backend setup code
        self.progress = None
        
    def run(self):
        # setup
        try:
            self.setup_gui()
            self.backend.setup()
            gtk.main()
        except YumexBackendFatalError,e:
            self.handle_error(e.err, e.msg)
            
    def handle_error(self,err,msg):        
        title =  _("Fatal Error")
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
        dialog = ErrorDialog(self.ui,self.window, title, text, longtext, modal=True)
        dialog.run()
        dialog.destroy()
        self.main_quit()
                    
        
    def process_queue(self):
        progress = self.get_progress()
        progress.set_pulse(True)        
        progress.show()        
        progress.set_title(_("Processing pending actions"))
        progress.set_header(_("Preparing the transaction"))
        queue = self.queue.queue
        for action in ('install','update','remove'):
            pkgs = queue.get(action[0])
            for po in pkgs:
                self.backend.transaction.add(po,action)
        tpkgs = self.backend.transaction.get_transaction_packages()
        for pkg in tpkgs:
            if pkg.action:
                self.info("   Package: %s Action: %s" % (pkg,pkg.action))
        if self.backend.transaction.process_transaction():
            self.debug("Transaction Completed OK")
            self.reload()
        else:
            self.debug("Transaction Failed")
        progress.hide()        
        progress.set_pulse(False)        

    def reload(self):
        ''' Reset current data and restart the backend '''
        self.backend.reset()                    # close the backend
        self.package_cache.reset()              # clear the package cache
        self.queue.queue.clear()                # clear the pending action queue
        self.populate_package_cache()           # repopulate the package cache
        self.notebook.set_active("package")     # show the package page
        self.ui.packageRadioUpdates.clicked()   # Select the updates package filter
                
    def run_test(self):
        def show(elems,desc=False):
            if elems:
                i = 0
                for el in elems:
                    i += 1
                    self.info("  %s" % str(el))
                    if desc:
                        self.info(el.description)
                    if i == 20:
                        break
        # get_packages
        self.progress.show()
        self.progress.set_header("Testing Yum Backend")
        self.progress.set_label("Getting Updated Packages")
        pkgs = self.backend.get_packages(FILTER.updates)
        #show(pkgs,True)
        self.progress.set_label("Getting Available Packages")
        pkgs = self.backend.get_packages(FILTER.available)
        #show(pkgs)
        for po in pkgs:
            if po.name == 'kdegames':
                break
        self.progress.set_label("Showing Filelist")
        self.info("Package : %s\n" % str(po))
        self.info("\nFiles:")
        i = 0
        for f in po.filelist:
            i += 1
            self.info("  %s" % f.strip('\n'))
            if i == 20: break
        num = 0    
        self.progress.set_label("Showing Changelog")
        self.info("\nChangelog")
        for (d,a,msg) in po.changelog:
            num += 1
            self.info(" %s %s" % (date.fromtimestamp(d).isoformat(),a))
            for line in msg.split('\n'):
                self.info("  %s" % line)
            if num == 3: break
        print    
        # Add to transaction for install
        self.backend.transaction.add(po,'install')
        tpkgs = self.backend.transaction.get_transaction_packages()
        show(tpkgs)
        # get_groups
        grps = self.backend.get_groups()
        show(grps)
        self.progress.set_label("Getting Repository information")
        # get_repositories
        repos = self.backend.get_repositories()
        for repo in repos:
            id,name,enabled,gpgckeck = repo
            self.info("%-50s : %s" % (id,enabled))
        # enable_repository
        repo = self.backend.enable_repository('updates',False)
        id,name,enabled,gpgckeck = repo
        self.info("%-50s : %s" % (id,enabled))        
        self.progress.hide()
        