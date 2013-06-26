# -*- coding: utf-8 -*-

'''Use Schemaker to generate colander schemas from SQLAlchemy models,
    one property/column at a time.
    '''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from sqlalchemy import func, types
import colander
import deform.widget as w

# import logging
# log = logging.getLogger(__name__)


class DBUniqueCheck(object):
    '''Generic colander validator to check that something is unique.'''
    def __init__(self, db, model_class, field, case_sensitive=True):
        self.db = db
        self.model_class = model_class
        self.field = field
        self.case_sensitive = case_sensitive

    def __call__(self, node, value):
        query = self.db.query(self.model_class)
        f = self.field
        v = value
        if not self.case_sensitive:
            f = func.lower(self.field)
            v = value.lower()
        if query.filter(f == v).scalar() is not None:
            s = ('A %s already exists with that %s'
                 % (self.model_class.__name__.lower(), node.name))
            raise colander.Invalid(node, s)


class DeferredDBCheck(colander.deferred):
    def __init__(self, valid_callable, **kwargs):
        self.valid_callable = valid_callable
        self.kwargs = kwargs

    def __call__(self, node, kwargs):
        db = kwargs['db']
        return self.valid_callable(db, **self.kwargs)


class DeferredAll(colander.deferred):
    def __init__(self, *validators):
        self.validators = list(validators)

    def __call__(self, node, kwargs):
        full = []
        for x in self.validators:
            if isinstance(x, colander.deferred):
                full.append(x(node, kwargs))
            else:
                full.append(x)
        return colander.All(*full)


def string_widget(prop, col, col_type, kw):
    '''Strategy for generating a widget for String types.'''
    maxlength = kw.pop('maxlength', None) or getattr(col_type, 'length', None)
    size = kw.pop('size', None)
    if size is None:  # If necessary, calculate a default size for the input
        size = int(maxlength if maxlength <= 35 else 35 + (maxlength - 35) / 4)
        if size > 60:
            size = 60
    return w.TextInputWidget(size=size, maxlength=maxlength,
        typ=kw.pop('input_type', 'text'), mask=kw.pop('mask', None),
        placeholder=kw.pop('placeholder', None),
    )


def enum_widget(prop, col, col_type, kw):
    choices = [(x, x.title()) for x in col_type.enums]
    return w.RadioChoiceWidget(values=choices)


class Schemaker(object):
    '''Configurable translator that creates a :class:`colander.SchemaNode`
        from a :class:`sqlalchemy.orm.properties.ColumnProperty`.

        You can change each aspect of the translator by overriding a method
        in a subclass.

        After instantiation you can manipulate the existing type_map.
        Each value in the map is a function that takes the column and returns
        a 2-tuple containing a colander type and a list of validators.

        Also after instantiation you can manipulate the widget_strategies map.
        It maps from colander types to callbacks that return a widget instance.

        Finally, use the configured object, by calling it multiple times to
        translate each SQLAlchemy model property into a colander SchemaNode.
        '''
    def __init__(self):
        self.type_map = {
            types.Boolean: lambda x: (colander.Boolean(), []),
            types.Date: lambda x: (colander.Date(), []),
            types.DateTime: lambda x: (colander.DateTime(), []),
            types.Time: lambda x: (colander.Time(), []),
            types.DECIMAL: lambda x: (colander.Decimal(), []),
            types.Numeric: lambda x: (colander.Decimal(), []),
            types.Float: lambda x: (colander.Float(), []),
            types.Integer: lambda x: (colander.Integer(), []),
            types.String: lambda x: (colander.String(), []),
            types.Unicode: lambda x: (colander.String(), []),
            types.Enum: lambda x: (colander.String(),
                                   [colander.OneOf(x.type.enums)]),
        }
        self.widget_strategies = {
            types.String: string_widget,
            types.Unicode: string_widget,
            types.Enum: enum_widget,
        }

    def get_type(self, column, column_type, kw):
        '''Get typ from kw or look up the type_map; also set validators.'''
        try:
            typ = kw.pop('typ')
        except KeyError:
            try:
                typ, validators = self.type_map[column_type.__class__](column)
            except KeyError:
                raise NotImplementedError(
                    'Unknown type: {}'.format(column_type))
        else:
            validators = kw.pop('validators', [])
        return typ, validators

    def get_label(self, prop):
        return prop.key.replace('_', ' ').capitalize()

    def get_default(self, column, col_type, kw):
        default = kw.pop('default', None)
        if default:
            return default
        elif column.default is None or not hasattr(column.default, 'arg') or \
                (isinstance(col_type, types.Integer) and
                column.primary_key and column.autoincrement):
            return colander.null
        elif column.default.is_callable:
            # Fix: SQLA wraps callables in lambda ctx: fn().
            return column.default.arg(None)
        else:
            return column.default.arg

    def get_missing(self, column, col_type, kw):
        if 'missing' in kw:
            return kw.pop('missing')
        elif not column.nullable and \
                not (isinstance(col_type, types.Integer) and
                column.primary_key and column.autoincrement):
            return colander.required
        elif not column.default is None and column.default.is_callable and \
                not (isinstance(col_type, types.Integer) and
                column.primary_key and column.autoincrement):
            # Fix: SQLA wraps default callables in lambda ctx: fn().
            return column.default.arg(None)
        elif not column.default is None and not column.default.is_callable \
                and not (isinstance(col_type, types.Integer) and
                column.primary_key and column.autoincrement):
            return column.default.arg
        else:
            return colander.null

    def __call__(self, prop, **kwargs):
        """Build and return a :class:`colander.SchemaNode` for a given Column.

            This method uses information stored in the ``info`` dictionary
            of the column. In other words,
            ``Colander`` options can be specified declaratively in
            ``SQLAlchemy`` models using the ``info`` argument that you can
            pass to :class:`sqlalchemy.Column`.

            Arguments/Keywords

            prop
                A given :class:`sqlalchemy.orm.properties.ColumnProperty`
                instance that represents the column being mapped.
            kw
                Override attributes of the schema.
            """
        kw = prop.info.copy()
        kw.update(kwargs)  # kwargs take precedence over the *info* dict
        del kwargs

        column = prop.property.columns[0]
        # Support sqlalchemy.types.TypeDecorator
        col_type = getattr(column.type, 'impl', column.type)
        # Obtain the colander type and an initial list of validators
        typ, validators = self.get_type(column, col_type, kw)

        # TODO Add unique checks
        # if col.primary_key:
        #     self._add_validator(
        #         kwargs, DeferredDBCheck(DBUniqueCheck,
        #                                 model_class=model_class,
        #                                 field=col))

        kwargs = dict(name=kw.pop('name', None) or prop.key,
                      title=kw.pop('title', None) or self.get_label(prop),
                      description=kw.pop('description', None),
                      default=self.get_default(column, col_type, kw),
                      missing=self.get_missing(column, col_type, kw),
                      validator=self.get_validator(col_type, kw, validators),
                      widget=self.get_widget(prop, column, col_type, kw))
        # kwargs.update(kw)
        # print(kwargs) # TODO Remove print
        return colander.SchemaNode(typ, **kwargs)

    def get_validator(self, col_type, kw, validators):
        maxlength = kw.get('maxlength') or getattr(col_type, 'length', None)
        if maxlength:
            validators.append(colander.Length(max=maxlength))
        more = kw.pop('validators', None)
        if more:
            validators.extend(more)
        if len(validators) == 0:
            return None
        elif len(validators) == 1:
            return validators[0]
        else:
            return colander.All(*validators)

    def get_widget(self, prop, column, col_type, kw):
        '''This default implementation either returns a widget that eventually
        has been passed to us, or looks up the widget_strategies map to
        generate a widget corresponding to the colander typ.
        '''
        widget = kw.pop('widget', None)
        if not widget:
            widget_maker = self.widget_strategies.get(col_type.__class__)
            if widget_maker:
                widget = widget_maker(prop, column, col_type, kw)
        return widget
