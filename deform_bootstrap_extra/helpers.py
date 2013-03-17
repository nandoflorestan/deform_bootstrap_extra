# -*- coding: utf-8 -*-

'''Helper functions for colander and deform.'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import colander as c
import deform.widget as w
from bag.sqlalchemy.tricks import length


def lengthen(max, min=0, size=None, widget_cls=w.TextInputWidget,
             typ='text', placeholder=None, validators=None):
    '''Use this to easily create well-sized inputs.

        Returns a dict containing *widget* and *validator*,
        all concerned about length.

        If the parameter *max* is not an integer, it is treated as a SQLALchemy
        model property from which the real *max* can be inferred.

        Example usage::

            from deform_bootstrap_extra.helpers import lengthen
            import colander as c

            class ContactSchema(CSRFSchema):
                name = c.SchemaNode(c.Str(), title=_("Name"), missing=None,
                    **lengthen(Contact.name))  # this is a model property
        '''
    if not isinstance(max, int):
        max = length(max)
    if not size:
        size = int(max if max <= 35 else 35 + (max - 35) / 4)
    if size > 60:
        size = 60
    validator = c.Length(min=min, max=max)
    if validators:
        validator = c.All(validator, *validators)
    return dict(widget=widget_cls(size=size, maxlength=max,
        placeholder=placeholder, typ=typ), validator=validator)
