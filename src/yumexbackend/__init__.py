
'''
'''

import pickle
import base64
from urlgrabber.progress import format_number


class YumexBackendBase(object):
    '''
    Yumex Backend Base class
    This is the base class to interact with the package system    
    '''
    def __init__(self, frontend, transaction):
        ''' 
        init the backend 
        @param frontend: the current frontend
        '''
        self.frontend = frontend
        self.transaction = transaction

    def setup(self, offline = False,repos=None):
        ''' Setup the backend'''
        raise NotImplementedError()

    def reset(self):
        ''' Reset the backend, so it can be setup again'''
        raise NotImplementedError()

    def get_packages(self, pkg_filter, show_dupes=False):
        ''' 
        get packages based on filter 
        @param pkg_filer: package list filter (Enum FILTER)
        @param show_dupes: show duplicate packages
        @return: a list of packages
        '''
        raise NotImplementedError()

    def get_repositories(self):
        ''' 
        get repositories 
        @return: a list of repositories
        '''
        raise NotImplementedError()

    def enable_repository(self, repoid, enabled = True):
        ''' 
        set repository enable state
        @param repoid: repo id to change
        @param enabled: repo enable state
        '''
        raise NotImplementedError()

    def get_groups(self):
        ''' 
        get groups 
        @return: a list of groups
        '''
        raise NotImplementedError()

    def get_group_packages(self, group, grp_filter):
        ''' 
        get packages in a group 
        @param group: group id to get packages from
        @param grp_filter: group filters (Enum GROUP)
        '''
        raise NotImplementedError()

    def search(self, keys, sch_filters):
        ''' 
        get packages matching keys
        @param keys: list of keys to seach for
        @param sch_filters: list of search filter (Enum SEARCH)
        '''
        raise NotImplementedError()

class YumexPackageBase:
    '''
    This is an abstract package object for a package in the package system
   '''

    def __init__(self, pkg):
        '''
        
        @param pkg:
        '''
        self._pkg = pkg
        self.selected = False

    def __str__(self):
        '''
        string representation of the package object
        '''
        return str(self._pkg)
      

    @property
    def name(self):
        '''
        
        '''
        return self._pkg.name

    @property
    def version(self):
        '''
        
        '''
        return self._pkg.ver

    @property
    def release(self):
        '''
        
        '''
        return self._pkg.rel

    @property
    def ver(self):
        '''
        
        '''
        return self._pkg.ver

    @property
    def rel(self):
        '''
        
        '''
        return self._pkg.rel

    @property
    def epoch(self):
        '''
        
        '''
        return self._pkg.epoch

    @property
    def arch(self):
        '''
        
        '''
        return self._pkg.arch

    @property
    def repoid(self):
        '''
        
        '''
        return self._pkg.repoid

    @property
    def action(self):
        '''
        
        '''
        return self._pkg.action

    @property
    def summary(self):
        '''
        
        '''
        return self._pkg.summary

    @property
    def description(self):
        ''' Package description '''
        raise NotImplementedError()

    @property
    def changelog(self):
        ''' Package changelog '''
        raise NotImplementedError()

    @property
    def filelist(self):
        ''' Package filelist '''        
        raise NotImplementedError()

    @property        
    def id(self):
        ''' Return the package id '''        
        return self._pkg.id

    @property
    def filename(self):
        ''' Package id (the full package filename) '''     
        return "%s-%s.%s.%s.rpm" % (self.name, self.version, self.release, self.arch)

    @property
    def fullname(self):
        ''' Package fullname  '''        
        self._pkg.fullname
            
    @property
    def fullver (self):
        '''
        Package full version-release
        '''
        return "%s-%s" % (self.version, self.release)
 
    def is_installed(self):
        return self.repoid[0] == '@' or self.repoid == 'installed'

    @property
    def sizeBytes(self):
        '''
        
        '''
        return long(self._pkg.size)

    @property
    def size(self):
        '''
        
        '''
        return format_number(self.sizeBytes)
   

class YumexGroupBase:
    '''
    This is an abstract group object for a package in the package system
   '''

    def __init__(self, grp, category):
        '''
        
        @param grp:
        @param category:
        '''
        self._grp = grp
        self._category = category
        self.selected = False

    @property
    def id(self):
        ''' Group id '''
        pass

    @property
    def name(self):
        ''' Group name '''
        pass

    @property
    def summary(self):
        ''' Group summary '''
        pass

    @property
    def description(self):
        ''' Group description '''
        pass
    
    @property
    def category(self):
        ''' Group category '''
        pass
    

class YumexTransactionBase:
    '''
    This is a abstract transaction queue for storing unprocessed changes
    to the system and to process the transaction on the system.
    '''
    def __init__(self, backend, frontend):
        '''
        initialize the transaction queue
        @param backend: The current YumexBackend
        @param frontend: the current YumexFrontend
        '''
        self.backend = backend
        self.frontend = frontend

    def add(self, po, action):
        '''
        add a package to the queue
        @param po: package to add to the queue
        '''
        pass

    def remove(self, po):
        '''
        remove a package from the queue
        @param po: package to remove from the queue
        '''
        pass

    def reset(self):
        '''
        reset the transaction queue
        '''
        pass

    def has_item(self, po):
        '''
        check if a package is already in the queue
        @param po: package to check for
        '''
        pass

    def add_group(self, grp):
        '''
        Add a group to the queue
        @param grp: group to add to queue
        '''
        pass

    def remove_group(self, grp):
        '''
        Remove a group from the queue
        @param grp: group to add to queue
        '''
        pass

    def has_group(self, grp):
        '''
        Check if a group is in the  queue
        @param grp: group to check for
        '''
        pass
    
    def process_transaction(self):
        '''
        Process the packages and groups in the queue
        '''

    def get_transaction_packages(self):
        '''
        Get the current packages in the transaction queue
        '''

class YumHistoryTransaction:
    """ Holder for a history transaction. """

    def __init__(self, yht):
        self.tid              = yht.tid
        self.beg_timestamp    = yht.beg_timestamp
        self.beg_rpmdbversion = yht.beg_rpmdbversion
        self.end_timestamp    = yht.end_timestamp
        self.end_rpmdbversion = yht.end_rpmdbversion
        self.loginuid         = yht.loginuid
        self.return_code      = yht.return_code

    @property
    def id(self):
        return ":hist\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % \
               (self.tid, self.beg_timestamp, self.beg_rpmdbversion,\
                self.end_timestamp, self.end_rpmdbversion, self.loginuid, self.return_code )

class YumHistoryPackage:

    def __init__(self, yhp):
        self.name   = yhp.name
        self.epoch  = yhp.epoch
        self.ver    = yhp.version
        self.rel    = yhp.release
        self.arch   = yhp.arch
        if hasattr(yhp,"state"):
            self.state  = yhp.state
        else:
            self.state = ""
        self.installed  = yhp.state_installed
        
    @property
    def version(self):
        return self.ver
    
    @property
    def release(self):
        return self.rel


    @property
    def pkgtup(self):
        return (self.name, self.arch, self.epoch, self.ver, self.rel)
        

    def __str__(self):
        '''
        string representation of the package object
        '''
        return self.fullname
        
    @property
    def fullname(self):
        ''' Package fullname  '''        
        if self.epoch and self.epoch != '0':
            return "%s-%s:%s.%s.%s" % (self.name, self.epoch, self.ver, self.rel, self.arch)
        else:   
            return "%s-%s.%s.%s" % (self.name, self.ver, self.rel, self.arch)

    @property
    def fullver(self):
        ''' Package full ver  '''        
        if self.epoch and self.epoch != '0':
            return "%s:%s.%s" % ( self.epoch, self.ver, self.rel)
        else:   
            return "%s.%s" % ( self.ver, self.rel)

  
    @property
    def id(self):
        return ":histpkg\t%s\t%s\t%s\t%s\t%s" % \
               (self.name, self.epoch, self.ver, self.rel, self.arch)


class YumPackage:
    ''' Simple object to store yum package information '''
    def __init__(self, base, args):
        '''
        
        @param base:
        @param args:
        '''
        self.base = base
        self.name = args[0]
        self.epoch = args[1]
        self.ver = args[2]
        self.rel = args[3]
        self.arch = args[4]
        self.repoid = args[5]
        self.summary = unpack(args[6])
        self.action = unpack(args[7])
        self.size = args[8]
        self.recent = args[9]

    def __str__(self):
        '''
        string representation of the package object
        '''
        return self.fullname
        
    @property
    def fullname(self):
        ''' Package fullname  '''        
        if self.epoch and self.epoch != '0':
            return "%s-%s:%s-%s.%s" % (self.name, self.epoch, self.ver, self.rel, self.arch)
        else:   
            return "%s-%s-%s.%s" % (self.name, self.ver, self.rel, self.arch)

    @property        
    def id(self):        
        '''
        
        '''
        return '%s\t%s\t%s\t%s\t%s\t%s' % (self.name, self.epoch, self.ver, self.rel, self.arch, self.repoid)

    def get_attribute(self, attr):
        '''
        
        @param attr:
        '''
        return self.base.get_attribute(self.id, attr)
    
    def get_changelog(self, num):
        '''
        
        @param num:
        '''
        return self.base.get_changelog(self.id, num)
    
    def get_update_info(self):
        return self.base.get_update_info(self.id)
    
    # helper funtion to non string pack/unpack parameter to be transfer over the stdout pipe 
def pack(value):
    '''  Pickle and base64 encode an python object'''
    return base64.b64encode(pickle.dumps(value))
    
def unpack(value):
    '''  base64 decode and unpickle an python object'''
    return pickle.loads(base64.b64decode(value))

    

