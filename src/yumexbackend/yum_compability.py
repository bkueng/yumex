# -*- coding: utf-8 *-*



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

'''
yum methods needed by yumex, but not available in dnf
'''

def packagesNewestByName(pkgs):
    """ Does the same as PackageSack.returnNewestByName().
        Note that given: foo-1.i386; foo-2.i386 and foo-3.x86_64"""
    newest = {}
    for pkg in pkgs:
        key = pkg.name

        # Can't use pkg.__cmp__ because it takes .arch into account
        cval = 1
        if key in newest:
            cval = pkg.verCMP(newest[key][0])
        if cval > 0:
            newest[key] = [pkg]
        elif cval == 0:
            newest[key].append(pkg)
    ret = []
    for vals in newest.itervalues():
        ret.extend(vals)
    return ret
def packagesNewestByNameArch(pkgs):
    """ Does the same as PackageSack.returnNewestByNameArch()
        The last _two_ pkgs will be returned, not just one of them."""
    newest = {}
    for pkg in pkgs:
        key = (pkg.name, pkg.arch)
        if key in newest and pkg.verLE(newest[key]):
            continue
        newest[key] = pkg
    return newest.values()
