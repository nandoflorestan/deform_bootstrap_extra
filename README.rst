deform_bootstrap_extra
~~~~~~~~~~~~~~~~~~~~~~

Extra features for deform_bootstrap

This package:

* constitutes another layer on top of the great package *deform_boostrap*,
  which skins Deform with Twitter's "bootstrap" library:
  http://pypi.python.org/pypi/deform_bootstrap
* contains special widgets and functions for Deform.

Our bootstrap-compatible templates
==================================

Our alterations to the templates are in the "templates" subdirectory.

Here are the changes we've made:

* checkbox.pt: Allows you to pass a *text* argument to a Boolean schema, and
  the text appears on the right of the checkbox.
* form.pt: Squashes a bug where buttons would be rendered disabled.
* password.pt: Supports *maxlength* and *placeholder* and
  automatically sets *required*.
* textarea.pt: Supports *maxlength* and *placeholder* and
  automatically sets *required*.
* textinput.pt: Supports *maxlength* and *placeholder* and
  automatically sets *required*. Also supports any HTML5 input type --
  for instance, you can set widget.type to "email" when instantiating a
  TextInputWidget.

All this has been tested against deform_bootstrap 0.2.5.

Our new widgets
===============

* widgets.TagsWidget: Sets up a beautiful jQuery-Tags-Input which in
  turn comes from http://xoxco.com/projects/code/tagsinput/

Helper functions
================

button()
--------

Use this function in a Pyramid app to easily generate a Deform button with
translated title and optionally a bootstrap icon.

    from deform_bootstrap_extra.pyramid import button

lengthen()
----------

Forms containing all inputs with the same size are extremely boring to
look at. When the widths of the inputs vary, not only the user gets a
better idea of how much to type in them, but the screen looks much more
interesting and easier to scan visually.

The ``lengthen()`` function calculates input width based on the
maxlength (which can optionally be inferred from a SQLAlchemy model property).
Example usage::

    from deform_bootstrap_extra.helpers import lengthen
    import colander as c

    class ContactSchema(CSRFSchema):
        name = c.SchemaNode(c.Str(), title=_("Name"), missing=None,
            **lengthen(Contact.name))  # this is a model property

from_now_on()
-------------

This Colander validator only accepts a time in the future. Example::

    from deform_bootstrap_extra.schema import from_now_on
    import colander as c

    class PromotionSchema(CSRFSchema):
        scheduled = c.SchemaNode(c.DateTime(default_tzinfo=None),
            missing=c.null, title=_("Schedule"), validator=from_now_on)
        (...)

    sch = PromotionSchema().bind(request=self.request, now=datetime.utcnow())

Trilean
-------

A schema type that can represent true, false and null. Example::

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


Installation
============

Our preferred way of enabling the whole stack is this:

.. code-block:: python

    # DO NOT include('deform_bootstrap')
    config.include('deform_bootstrap_extra')

This sets deform up for i18n (configuring a translator function and pointing
colander and deform locale directories) and gives its template loader the
correct directory hierarchy, so it will search for templates first in
deform_bootstrap_extra, then in deform_bootstrap, finally in deform.

Contribute
==========

You can help development at
https://github.com/nandoflorestan/deform_bootstrap_extra
