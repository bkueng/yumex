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

import gtk
import gobject
import logging
import pango

from yumexbase import *
from yumexbase.i18n import _
from yum.misc import sortPkgObj

class SelectionView:
    def __init__(self,widget):
        self.view = widget
        self.store = None

    def create_text_column_num( self, hdr,colno,resize = True):
        cell = gtk.CellRendererText()    # Size Column
        column = gtk.TreeViewColumn( hdr, cell, text=colno )
        column.set_resizable(resize )
        self.view.append_column( column )        

    def create_text_column( self, hdr, property, size,sortcol = None):
        """ 
        Create a TreeViewColumn with text and set
        the sorting properties and add it to the view
        """
        cell = gtk.CellRendererText()    # Size Column
        column = gtk.TreeViewColumn( hdr, cell )
        column.set_resizable( True )
        column.set_cell_data_func( cell, self.get_data_text, property )
        column.set_sizing( gtk.TREE_VIEW_COLUMN_FIXED )
        column.set_fixed_width( size )
        column.set_sort_column_id( -1 )            
        self.view.append_column( column )        
        return column

    def create_selection_colunm(self,attr ):
        # Setup a selection column using a object attribute 
        cell1 = gtk.CellRendererToggle()    # Selection
        cell1.set_property( 'activatable', True )
        column1 = gtk.TreeViewColumn( "", cell1 )
        column1.set_cell_data_func( cell1, self.get_data_bool, attr )
        column1.set_sizing( gtk.TREE_VIEW_COLUMN_FIXED )
        column1.set_fixed_width( 20 )
        column1.set_sort_column_id( -1 )            
        self.view.append_column( column1 )
        cell1.connect( "toggled", self.on_toggled )            
        column1.set_clickable( True )

    def create_selection_column_num(self,num ):
        # Setup a selection column using a column num
        cell1 = gtk.CellRendererToggle()    # Selection
        cell1.set_property( 'activatable', True )
        column1 = gtk.TreeViewColumn( "    ", cell1 )
        column1.add_attribute( cell1, "active", num )
        column1.set_resizable( True )
        column1.set_sort_column_id( -1 )            
        self.view.append_column( column1 )
        cell1.connect( "toggled", self.on_toggled )     
        
    def get_data_text( self, column, cell, model, iter,property ):
        obj = model.get_value( iter, 0 )
        if obj:
            cell.set_property( 'text', getattr( obj, property ) )
            cell.set_property('foreground',obj.color)

    def get_data_bool( self, column, cell, model, iter, property ):
        obj = model.get_value( iter, 0 )
        cell.set_property( "visible", True )
        if obj:
            cell.set_property( "active", getattr( obj, property ) )
            

    def on_toggled(self,widget,path):
        ''' 
        selection togged handler
        overload in child class
        '''
        pass
    
class YumexPackageView(SelectionView):
    def __init__( self, widget,qview ):
        SelectionView.__init__(self, widget)
        self.view.modify_font(SMALL_FONT)
        self.headers = [_( "Package" ), _( "Ver" ), _( "Summary" ), _( "Repo" ), _( "Architecture" ), _( "Size" )]
        self.store = self.setupView()
        self.queue = qview.queue
        self.queueView = qview
        
    def setupView( self ):
        store = gtk.ListStore( gobject.TYPE_PYOBJECT,str)
        self.view.set_model( store )
        self.create_selection_colunm('selected')
        # Setup resent column
        cell2 = gtk.CellRendererPixbuf()    # new
        cell2.set_property( 'stock-id', gtk.STOCK_ADD )
        column2 = gtk.TreeViewColumn( "", cell2 )
        column2.set_cell_data_func( cell2, self.new_pixbuf )
        column2.set_sizing( gtk.TREE_VIEW_COLUMN_FIXED )
        column2.set_fixed_width( 20 )
        column2.set_sort_column_id( -1 )            
        self.view.append_column( column2 )
        column2.set_clickable( True )

        self.create_text_column( _( "Package" ), 'name' , size=200)
        self.create_text_column( _( "Ver." ), 'version', size = 80 )
        self.create_text_column( _( "Arch." ), 'arch' , size = 60 )
        self.create_text_column( _( "Summary" ), 'summary', size=400 )
        self.create_text_column( _( "Repo." ), 'repoid' , size=90 )
        self.create_text_column( _( "Size." ), 'size' , size=90)
        self.view.set_search_column( 1 )
        self.view.set_enable_search(True)
        #store.set_sort_column_id(1, gtk.SORT_ASCENDING)
        self.view.set_reorderable( False )
        return store
   
    
    def on_toggled( self, widget, path ):
        """ Package selection handler """
        iter = self.store.get_iter( path )
        obj = self.store.get_value( iter, 0 )
        self.togglePackage(obj)
        self.queueView.refresh()
        
    def togglePackage(self,obj):
        if obj.queued == obj.action:
            obj.queued = None
            self.queue.remove(obj)
        else:
           obj.queued = obj.action      
           print "QUEUE: ", obj.name,obj.action
           self.queue.add(obj)
        obj.set_select( not obj.selected )
        
                
    def selectAll(self):
        for el in self.store:
            obj = el[0]
            if not obj.queued == obj.action:
                obj.queued = obj.action      
                self.queue.add(obj)
                obj.set_select( not obj.selected )
        self.queueView.refresh()
        self.view.queue_draw() 

    def deselectAll(self):
        for el in self.store:
            obj = el[0]
            if obj.queued == obj.action:
                obj.queued = None
                self.queue.remove(obj)
                obj.set_select( not obj.selected )
        self.queueView.refresh()
        self.view.queue_draw() 

    def new_pixbuf( self, column, cell, model, iter ):
        """ 
        Cell Data function for recent Column, shows pixmap
        if recent Value is True.
        """
        pkg = model.get_value( iter, 0 )
        if pkg:
            action = pkg.queued
            if action:            
                if action in ( 'u', 'i' ):
                    icon = 'network-server'
                else:
                    icon = 'edit-delete'
                cell.set_property( 'visible', True )
                cell.set_property( 'icon-name', icon )
            else:
                cell.set_property( 'visible', pkg.recent )
                cell.set_property( 'icon-name', 'document-new' )
        else:
            cell.set_property( 'visible', False )
            

    def get_selected( self, package=True ):
        """ Get selected packages in current packageList """
        selected = []
        for row in self.store:
            col = row[0]
            if col:
                pkg = row[0][0]
                if pkg.selected:
                    selected.append( pkg )
        return selected
    
    def add_packages(self,pkgs,progress=None):
        self.store.clear()
        queued = self.queue.get()
        if pkgs:
            pkgs.sort(sortPkgObj)
            self.view.set_model(None)
            for po in pkgs:
                self.store.append([po,str(po)])
                if po in queued[po.action]:
                    po.queued = po.action
                    po.set_select(True)
            self.view.set_model(self.store)
        

class YumexQueue:
    def __init__(self):
        self.logger = logging.getLogger('yumex.YumexQueue')
        self.packages = {}
        self.packages['i']= []
        self.packages['u'] = []
        self.packages['r'] = []
        self.groups = {}
        self.groups['i'] = []
        self.groups['r'] = []

    def clear( self ):
        del self.packages
        self.packages = {}
        self.packages['i'] = []
        self.packages['u'] = []
        self.packages['r'] = []
        self.groups = {}
        self.groups['i'] = []
        self.groups['r'] = []
        
    def get( self, action = None ):        
        if action == None:
            return self.packages
        else:
            return self.packages[action]
            
    def total(self):
        return len(self.packages['i'])+len(self.packages['u'])+len(self.packages['r'])
        
    def add( self, pkg):
        list = self.packages[pkg.action]
        if not pkg in list:
            list.append( pkg )
        self.packages[pkg.action] = list

    def remove( self, pkg):
        list = self.packages[pkg.action]
        if pkg in list:
            list.remove( pkg )
        self.packages[pkg.action] = list

    def addGroup( self, grp, action):
        list = self.groups[action]
        if not grp in list:
            list.append( grp )
        self.groups[action] = list

    def removeGroup( self, grp, action):
        list = self.groups[action]
        if grp in list:
            list.remove( grp )
        self.groups[action] = list

    def hasGroup(self,grp):
        for action in ['i','r']:
            if grp in self.groups[action]:
                return action
        return None
        
    def dump(self):
        self.logger.info(_("Package Queue:"))
        for action in ['install','update','remove']:
            a = action[0]
            list = self.packages[a]
            if len(list) > 0:
                self.logger.info(_(" Packages to %s" % action))
                for pkg in list:
                    self.logger.info(" ---> %s " % str(pkg))
        for action in ['install','remove']:
            a = action[0]
            list = self.groups[a]
            if len(list) > 0:
                self.logger.info(_(" Groups to %s" % action))
                for grp in list:
                    self.logger.info(" ---> %s " % grp)
            
    def getParser(self):
        cp = YumexQueueFile()
        for action in ['install','update','remove']:
            a = action[0]
            list = self.packages[a]
            if len(list) > 0:
                for pkg in list:
                    cp.setPO(action,pkg)      
        return cp

        
class YumexQueueView:
    """ Queue View Class"""
    def __init__( self, widget):
        self.view = widget
        self.view.modify_font(SMALL_FONT)
        self.model = self.setup_view()
        self.queue = YumexQueue()

    def setup_view( self ):
        """ Create Notebook list for single page  """
        model = gtk.TreeStore( gobject.TYPE_STRING, gobject.TYPE_STRING )           
        self.view.set_model( model )
        cell1 = gtk.CellRendererText()
        column1= gtk.TreeViewColumn( _( "Packages" ), cell1, markup=0 )
        column1.set_resizable( True )
        self.view.append_column( column1 )

        cell2 = gtk.CellRendererText()
        column2= gtk.TreeViewColumn( _( "Summary" ), cell2, text=1 )
        column2.set_resizable( True )
        self.view.append_column( column2 )
        model.set_sort_column_id( 0, gtk.SORT_ASCENDING )
        self.view.get_selection().set_mode( gtk.SELECTION_MULTIPLE )
        return model
    
    def deleteSelected( self ):
        rmvlist = []
        model, paths = self.view.get_selection().get_selected_rows()
        for p in paths:
            row = model[p]
            if row.parent != None:
                rmvlist.append( row[0] )
        for pkg in self.getPkgsFromList( rmvlist ):
            pkg.queued = None
            pkg.set_select( not pkg.selected )
        f = lambda x: str( x ) not in rmvlist
        for action in ['u', 'i', 'r']:
            list = self.queue.get(action)
            if list:
                self.queue.packages[action] = filter( f, list )
        self.refresh()


    def getPkgsFromList( self, rlist ):
        rclist = []
        f = lambda x: str( x ) in rlist
        for action in ['u', 'i', 'r']:
            list = self.queue.packages[action]
            if list:
                rclist += filter( f, list )
        return rclist
        
    def refresh ( self ):
        """ Populate view with data from queue """
        self.model.clear()
        label = _( "<b>Packages To Update</b>" )
        list = self.queue.packages['u']
        if len( list ) > 0:
            self.populate_list( label, list )
        label = _( "<b>Packages To Install</b>" )
        list = self.queue.packages['i']
        if len( list ) > 0:
            self.populate_list( label, list )
        label = _( "<b>Packages To Remove</b>" )
        list = self.queue.packages['r']
        if len( list ) > 0:
            self.populate_list( label, list )
        self.view.expand_all()
            
    def populate_list( self, label, list ):
        parent = self.model.append( None, [label, ""] )
        for pkg in list:
            self.model.append( parent, [str( pkg ), pkg.summary] )

class YumexRepoView(SelectionView):
    """ 
    This class controls the repo TreeView
    """
    def __init__( self, widget):
        SelectionView.__init__(self, widget)
        self.view.modify_font(SMALL_FONT)        
        self.headers = [_('Repository'),_('Filename')]
        self.store = self.setup_view()
    
    
    def on_toggled( self, widget, path):
        """ Repo select/unselect handler """
        iter = self.store.get_iter( path )
        state = self.store.get_value(iter,0)
        self.store.set_value(iter,0, not state)
                     
    def setup_view( self ):
        """ Create models and columns for the Repo TextView  """
        store = gtk.ListStore( 'gboolean', gobject.TYPE_STRING,gobject.TYPE_STRING,'gboolean')
        self.view.set_model( store )
        # Setup Selection Column
        self.create_selection_column_num(0)
        # Setup resent column
        cell2 = gtk.CellRendererPixbuf()    # gpgcheck
        cell2.set_property( 'stock-id', gtk.STOCK_DIALOG_AUTHENTICATION )
        column2 = gtk.TreeViewColumn( "", cell2 )
        column2.set_cell_data_func( cell2, self.new_pixbuf )
        column2.set_sizing( gtk.TREE_VIEW_COLUMN_FIXED )
        column2.set_fixed_width( 20 )
        column2.set_sort_column_id( -1 )            
        self.view.append_column( column2 )
        column2.set_clickable( True )
               
        # Setup reponame & repofile column's
        self.create_text_column_num( _('Repository'),1 )
        self.create_text_column_num( _('Name'),2 )
        self.view.set_search_column( 1 )
        self.view.set_reorderable( False )
        return store
    
    def populate( self, data, showAll=False ):
        """ Populate a repo liststore with data """
        self.store.clear()
        for state,id,name,gpg in data:
            if not self.isHidden(id) or showAll:
                self.store.append([state,id,name,gpg])     
            
    def isHidden(self,id):
        for hide in REPO_HIDE:
            if hide in id:
                return True
        else:
            return False                  

    def new_pixbuf( self, column, cell, model, iter ):
        gpg = model.get_value( iter, 3 )
        if gpg:
            cell.set_property( 'visible', True )
        else:
            cell.set_property( 'visible',False)
            
    def get_selected( self ):
        selected = []
        for elem in self.store:
            state = elem[0]
            name = elem[1]
            if state:
                selected.append( name )
        return selected
        
    def get_notselected( self ):
        notselected = []
        for elem in self.store:
            state = elem[0]
            name = elem[1]
            if not state:
                notselected.append( name )
        return notselected
            
    def deselect_all( self ):
        iterator = self.store.get_iter_first()
        while iterator != None:    
            self.store.set_value( iterator, 0, False )
            iterator = self.store.iter_next( iterator )

    def select_all( self ):
        iterator = self.store.get_iter_first()
        while iterator != None:    
            self.store.set_value( iterator, 0, True )
            iterator = self.store.iter_next( iterator )
            

    def select_by_keys( self, keys):
        self.store 
        iterator = self.store.get_iter_first()
        while iterator != None:    
            repoid = self.store.get_value( iterator, 1 )
            if repoid in keys:
                self.store.set_value( iterator, 0, True )
            else:
                self.store.set_value( iterator, 0, False)
            iterator = self.store.iter_next( iterator )
