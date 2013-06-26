# -*- coding: utf-8 -*-

'''More generic schema stuff (types and validators) for Colander.'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import colander as c
import re
from nine import str
try:
    from .pyramid import _
except ImportError:
    _ = str  # and i18n is disabled.


@c.deferred
def from_now_on(node, kw):
    '''Validator that only accepts a time in the future. Example::

    from deform_bootstrap_extra.schema import from_now_on
    import colander as c

    class PromotionSchema(CSRFSchema):
        scheduled = c.SchemaNode(c.DateTime(default_tzinfo=None),
            missing=c.null, title=_("Schedule"), validator=from_now_on)
        (...)

    sch = PromotionSchema().bind(request=self.request, now=datetime.utcnow())
    '''
    return c.Range(min=kw['now'],
        # min_err=_('${val} is in the past. Current time is ${min}'))
        min_err=_('Cannot be in the past. Current time is ${min}'))


def regex_validator(node, value):
    '''Validator that ensures a regular expression can be compiled.'''
    try:
        re.compile(value)
    except Exception as e:
        raise c.Invalid(node, _("Invalid regular expression: {}")
            .format(str(e)))


class Trilean(c.SchemaType):
    """A type that can represent true, false and null. Example::

    from deform_bootstrap_extra.schema import Trilean
    import colander as c
    import deform.widget as w

    class ContactSchema(CSRFSchema):
        (...)
        male = c.SchemaNode(Trilean(), title=_("Sex"), missing=None,
            widget=w.SelectWidget(values=[
                (c.null, _("- Choose -")),
                ('false', _("Female")),
                ('true', _("Male")),
        ]))
    """
    def serialize(self, node, appstruct):
        if appstruct is c.null:
            return c.null
        return appstruct and 'true' or 'false'

    def deserialize(self, node, cstruct):
        if cstruct in ('<colander.null>', c.null):
            return c.null
        try:
            result = str(cstruct)
        except:
            raise c.Invalid(node,
                _('${val} is not a string', mapping={'val': cstruct}))
        result = result.lower()
        if result in ('false', '0'):
            return False
        return True
