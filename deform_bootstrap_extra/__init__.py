# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def includeme(config):
    '''Hook for Pyramid web applications. The actual code is in another module;
    this way users of other web frameworks don't need to import Pyramid.
    '''
    from .pyramid import setup_for_pyramid
    setup_for_pyramid(config)


def monkeypatch_colander():
    '''Alter Colander to introduce the more useful asdict2() method.'''
    print('Adding asdict2() to Colander.')
    import colander as c

    def asdict2(self):
        """Also returns a dictionary containing a basic
        (non-language-translated) error report for this exception.

        ``asdict`` returns a dictionary containing fewer items -- the keys
        refer only to the leaves. This method returns a dictionary with
        more items: one key for each node that has an error,
        regardless of whether the node is a leaf or an ancestor.
        This way you can place error messages on more places of a form.

        In my application I want to display messages on parents
        as well as leaves... I am not using Deform in this case...
        """
        paths = self.paths()
        errors = []
        for path in paths:  # Each path is a tuple of Invalid instances.
            keyparts = []
            for exc in path:
                keyname = exc._keyname()
                if keyname:
                    keyparts.append(keyname)
                for msg in exc.messages():
                    errors.append(('.'.join(keyparts), msg))
        errors = set(errors)  # Filter out repeats
        adict = {}
        for key, msg in errors:
            if key in adict:
                adict[key] = adict[key] + '; ' + msg
            else:
                adict[key] = msg
        return adict
    c.Invalid.asdict2 = asdict2
