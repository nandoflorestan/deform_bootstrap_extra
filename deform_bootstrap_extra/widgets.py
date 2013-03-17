# -*- coding: utf-8 -*-

'''More widgets for Deform.'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import deform.widget as w


class TagsWidget(w.TextInputWidget):
    '''This widget depends on xoxco's jQuery-Tags-Input.

        Usage::

            widget = TagsWidget(autocomplete_url='/some/url')
        '''
    template = 'xoxco_tags'
    height = 'auto'
    width = 'auto'


"""
class SlugWidget(w.TextInputWidget):
    '''Lets you pass a *prefix* which will appear just before the <input>.
    TODO: This feature is probably no longer necessary
    since deform_bootstrap has *input_prepend* and *input_append*.
    '''
    # TODO: Make the slug input reflect the content of another input
    template = 'slug'
"""
