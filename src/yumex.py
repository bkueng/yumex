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

# Yumex main 

import sys
import os
from yumexgui import YumexApplication

if os.environ.has_key('YUMEX_BACKEND') and os.environ['YUMEX_BACKEND'] == 'dummy':
    from yumexbackend.dummy_backend import YumexBackendDummy as backend 
else:
    from yumexbackend.yum_backend import YumexBackendYum as backend 
    
app = YumexApplication(backend)
#app.run_test()
app.run()
    

sys.exit(0)
