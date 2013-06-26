# -*- coding: utf-8 -*-

'Functions to set up and more easily use deform_bootstrap_extra with Pyramid.'

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import deform as d
# from pkg_resources import resource_filename  # does not work in appengine 177
from pyramid.asset import abspath_from_asset_spec
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request

from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('deform_bootstrap_extra')
del TranslationStringFactory


def translator(term):
    return get_localizer(get_current_request()).translate(term)


already_setup = False


def setup_for_pyramid(config, translator=translator, template_dirs=(
                      'deform_bootstrap_extra:templates',
                      'deform_bootstrap:templates',
                      'deform:templates')):
    '''Set deform up for i18n and give its template loader the correct
    directory hierarchy.

    This includes deform_bootstrap, so the app developer must not.
    '''
    global already_setup
    if already_setup:
        return
    from .. import monkeypatch_colander
    monkeypatch_colander()

    config.add_translation_dirs('colander:locale', 'deform:locale',)
    #    'deform_bootstrap_extra:locale')
    config.add_static_view('deform', 'deform:static')
    config.add_static_view('deform_bootstrap_extra',
        'deform_bootstrap_extra:static')
    config.include('deform_bootstrap')
    # dirs = tuple([resource_filename(*dir.split(':'))
    #     for dir in template_dirs])
    dirs = tuple([abspath_from_asset_spec(dir) for dir in template_dirs])
    d.Form.set_zpt_renderer(dirs, translator=translator)
    already_setup = True


def button(title=_('Submit'), name=None, icon=None):
    '''Conveniently generate a Deform button while setting its
    ``name`` attribute, translating the label and capitalizing it.

    The button may also have a bootstrap icon.
    '''
    b = d.Button(title=translator(title).capitalize(),
                 name=name or title.lower())
    b.icon = icon
    return b


def verify_csrf(func):
    '''Decorator that checks the CSRF token. TODO: Use and test.'''
    def wrapper(*a, **kw):
        request = get_current_request()
        if request.params.get('_csrf_') == request.session.get_csrf_token():
            return func(*a, **kw)
        else:
            raise HTTPUnauthorized('You do not pass our CSRF protection.')
    return wrapper
