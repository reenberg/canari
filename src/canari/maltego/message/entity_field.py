"""Entity fields are build as descriptor objects[1].

Each entity field defines the magic functions __get__ and __set__.  An easy
examples of unit conversion more or less demonstrates how this works for our
entity fields.


    class Meter(object):
        '''Descriptor for a meter.'''

        def __init__(self, value=0.0):
            self.value = float(value)
        def __get__(self, instance, owner):
            return self.value
        def __set__(self, instance, value):
            self.value = float(value)

    class Foot(object):
        '''Descriptor for a foot.'''

        def __get__(self, instance, owner):
            return instance.meter * 3.2808
        def __set__(self, instance, value):
            instance.meter = float(value) / 3.2808

    class Distance(object):
        '''Class to represent distance holding two descriptors for feet and
        meters.'''
        meter = Meter(10)
        foot = Foot()

    In [28]: d = Distance()

    In [29]: d.meter
    Out[29]: 10.0

    In [30]: d.foot
    Out[30]: 32.808


In our case, an instance of the entity field type (descriptor object) is stored
under its property name on the entity class, and a mapping from the field name
to property name is stored in the _fields_to_properties_ dictionary on the
object as well.  So for example when we decorate the base class Entity, with
@EntityField to create the notes property:

  @EntityField(name='notes#', propname='notes', link=True, matchingrule=MatchingRule.Loose)

we end up having a notes attribute on the Entity class, which is an instance of
the StringEntityField descriptor, and an entry of {'notes#': 'notes'} in the
_fields_to_properties_ dictionary.  When trying to read from the notes attribute
we invoke the magic function __get__ on the StringEntityField which will test if
'notes#' is in the fields attribute of our Entity instance and return it, or
return None.  When setting a value we invoke the magic function __set__ on the
StringEntityField which will delete the element from the fields attributes if
the value is None or it will create a new AdditionalField instance with the
properties from the @EntityField decorator and with the value supplied.


  [1]: http://www.rafekettler.com/magicmethods.html#descriptor

"""

import re
from numbers import Number
from datetime import (
    datetime,
    date,
    timedelta,
)


from canari.maltego.message.common import (
    AdditionalField,
    MatchingRule,
)


class StringEntityField(object):
    def __init__(self, name, displayname=None, decorator=None,
                 matchingrule=MatchingRule.Strict, is_value=False,
                 **extras):
        self.decorator = decorator
        self.is_value = is_value
        self.name = name
        self.displayname = displayname
        self.matchingrule = matchingrule

    def __get__(self, obj, objtype):
        if self.is_value:
            return obj.value
        elif self.name in obj.fields:
            return obj.fields[self.name].value
        return None

    def __set__(self, obj, val):
        if self.is_value:
            obj.value = val
        elif not val and self.name in obj.fields:
            del obj.fields[self.name]
        else:
            if self.name not in obj.fields:
                obj.fields[self.name] = AdditionalField(
                    name=self.name,
                    value=val,
                    displayname=self.displayname,
                    matchingrule=self.matchingrule
                )
            else:
                obj.fields[self.name].value = val
        if callable(self.decorator):
            self.decorator(obj, val)


class EnumEntityField(StringEntityField):
    def __init__(self, name, displayname=None, choices=None, decorator=None,
                 matchingrule=MatchingRule.Strict, is_value=False,
                 **extras):
        self.choices = [str(c) if not isinstance(c, basestring) else c
                        for c in choices or []]
        super(EnumEntityField, self).__init__(name, displayname, decorator,
                                              matchingrule, is_value)

    def __set__(self, obj, val):
        val = str(val) if not isinstance(val, basestring) else val
        if val not in self.choices:
            raise ValueError('Expected one of %s (got %s instead)' %
                             (self.choices, val))
        super(EnumEntityField, self).__set__(obj, val)


class IntegerEntityField(StringEntityField):
    def __get__(self, obj, objtype):
        i = super(IntegerEntityField, self).__get__(obj, objtype)
        return int(i) if i is not None else None

    def __set__(self, obj, val):
        if not isinstance(val, Number):
            raise TypeError('Expected an instance of int (got %s instance instead)' %
                            type(val).__name__)
        super(IntegerEntityField, self).__set__(obj, val)


class BooleanEntityField(StringEntityField):
    def __get__(self, obj, objtype):
        b = super(BooleanEntityField, self).__get__(obj, objtype)
        return b.startswith('t') or b == '1' if b is not None else None

    def __set__(self, obj, val):
        if not isinstance(val, bool):
            raise TypeError('Expected an instance of bool (got %s instance instead)' %
                            type(val).__name__)
        super(BooleanEntityField, self).__set__(obj, str(val).lower())


class FloatEntityField(StringEntityField):
    def __get__(self, obj, objtype):
        f = super(FloatEntityField, self).__get__(obj, objtype)
        return float(f) if f is not None else None

    def __set__(self, obj, val):
        if not isinstance(val, Number):
            raise TypeError('Expected an instance of float (got %s instance instead)' %
                            type(val).__name__)
        super(FloatEntityField, self).__set__(obj, val)


class LongEntityField(StringEntityField):
    def __get__(self, obj, objtype):
        l = super(LongEntityField, self).__get__(obj, objtype)
        return long(l) if l is not None else None

    def __set__(self, obj, val):
        if not isinstance(val, Number):
            raise TypeError('Expected an instance of float (got %s instance instead)' %
                            type(val).__name__)
        super(LongEntityField, self).__set__(obj, val)


class DateTimeEntityField(StringEntityField):
    def __get__(self, obj, objtype):
        d = super(DateTimeEntityField, self).__get__(obj, objtype)
        return datetime.strptime(d, '%Y-%m-%d %H:%M:%S.%f') if d is not None else None

    def __set__(self, obj, val):
        if not isinstance(val, datetime):
            raise TypeError('Expected an instance of datetime (got %s instance instead)' %
                            type(val).__name__)
        super(DateTimeEntityField, self).__set__(obj, val)


class DateEntityField(StringEntityField):
    def __get__(self, obj, objtype):
        d = super(DateEntityField, self).__get__(obj, objtype)
        return datetime.strptime(d, '%Y-%m-%d').date() if d is not None else None

    def __set__(self, obj, val):
        if not isinstance(val, date):
            raise TypeError('Expected an instance of date (got %s instance instead)' %
                            type(val).__name__)
        super(DateEntityField, self).__set__(obj, val)


class timespan(timedelta):
    matcher = re.compile(r'(\d+)d (\d+)h(\d+)m(\d+)\.(\d+)s')

    def __str__(self):
        return '%dd %dh%dm%d.%03ds' % (
            abs(self.days),
            int(self.seconds) // 3600,
            int(self.seconds) % 3600 // 60,
            int(self.seconds) % 60,
            int(self.microseconds)
        )

    @classmethod
    def fromstring(cls, ts):
        m = cls.matcher.match(ts)
        if m is None:
            raise ValueError('Time span must be in "%%dd %%Hh%%Mm%%S.%%fs" format')
        days, hours, minutes, seconds, useconds = [int(i) for i in m.groups()]
        return timespan(days, (hours * 3600) + (minutes * 60) + seconds,
                        useconds)


class TimeSpanEntityField(StringEntityField):
    def __get__(self, obj, objtype):
        d = super(TimeSpanEntityField, self).__get__(obj, objtype)
        return timespan.fromstring(d) if d is not None else None

    def __set__(self, obj, val):
        if not isinstance(val, timespan) or not isinstance(val, timedelta):
            raise TypeError('Expected an instance of timedelta (got %s instance instead)' %
                            type(val).__name__)
        if val.__class__ is timedelta:
            val = timespan(val.days, val.seconds, val.microseconds)
        super(TimeSpanEntityField, self).__set__(obj, val)


class RegexEntityField(StringEntityField):
    def __init__(self, name, displayname=None, pattern='.*', decorator=None,
                 matchingrule=MatchingRule.Strict, is_value=False,
                 **extras):
        super(RegexEntityField, self).__init__(name, displayname, decorator,
                                               matchingrule, is_value, **extras)
        self.pattern = re.compile(pattern)

    def __set__(self, obj, val):
        if not isinstance(val, basestring):
            val = str(val)
        if not self.pattern.match(val):
            raise ValueError('Failed match for %s, expected pattern %s instead.' %
                             (repr(val), repr(self.pattern.pattern)))
        super(RegexEntityField, self).__set__(obj, val)


class ColorEntityField(RegexEntityField):
    def __init__(self, name, displayname=None, decorator=None,
                 matchingrule=MatchingRule.Strict, is_value=False,
                 **extras):
        super(ColorEntityField, self).__init__(
            name, displayname, '^#[0-9a-fA-F]{6}$',
            decorator, matchingrule, is_value, **extras
        )



class EntityFieldType:
    String = StringEntityField
    Integer = IntegerEntityField
    Long = LongEntityField
    Float = FloatEntityField
    Bool = BooleanEntityField
    Enum = EnumEntityField
    Date = DateEntityField
    DateTime = DateTimeEntityField
    TimeSpan = TimeSpanEntityField
    Color = ColorEntityField


class EntityField(object):
    """Function decorator to define 'additional fields' on an Entity.

    This is used to define notes, bookmarks, link style, (additional)
    properties, etc, of the entity.

    """
    def __init__(self, name, displayname=None, propname=None,
                 matchingrule=MatchingRule.Strict,
                 type=EntityFieldType.String,
                 required=False, decorator=None, is_value=False,
                 **kwargs):
        """Arguments:

- name: The 'Name' attribute of the output XML.  Should be unique and
    distinguishes this field from any other field, without spaces.  Dots (.) are
    widely used to form a unique namespace this field belongs to.

    * Required in XML: True

- displayname: (Optional) The 'DisplayName' attribute of the output XML.  Used
    for fields that are shown to the user inside the Maltego client, such as the
    (additional) properties of an entity.  If no display name is given, then the
    'Name' attribute is shown to the user.

    * Default: None
    * Required in XML: False

- propname: (Optionale) The Python property that gets associated with this field
    on the Entity.  This may be used to assosiated the property 'notes' with
    special Maltego field name 'notes#', such that one may set/get the notes
    values on an entity by:

        import canari.maltego.entities
        p = canari.maltego.entities.Person
        p.notes = "foo bar baz"

    NOTE: This field is required if the 'name' argument contains dots, or else
    it will not be accessible!

    If this is not defined, then the 'name' argument will be used with all white
    space replaced with underscores ('_').

    * Default: Capitalised 'name' argument

- matchingrule: (Optional) The 'MatchingRule' attribute of the output XML.  Used
    to determine whether or not this field have any influence when determining
    if two entities should be merged.

    * Default: MatchingRule.Strict
    * Required in XML: False

- type: (Optional) The data type of the field.  See the respective
    EntityFieldType's implementation for a reference of how they parse and validates data.

    * Default: EntityFieldType.String

- required: (Optional) Specifies whether the field must be filled out with a
    value or not, before being sent back to the Maltego client.

    * Default: False

- choices: (Optional) A list of acceptable values for this field.  This is
  solely used by the EntityFieldType.Enum type.  If this is not specified, then
  it won't be possible to set a value on a Enum field type, and a ValueError is
  thrown instead.

    * Default: None

- decorator: (Optional) A function that is invoked each and everytime the
    field's value is set or changed.

    * Default: None


- is_value: (Optional) A boolean value that determines whether the field is also
    the default value of the entity object.

    * Default: False


- link: (Deprecated) Boolean describing whether or not this field has a display
    name.  This was typically used by the all the link fields (label, color,
    style, etc), but it was misused and removing it makes the logic more clean.

        """
        self.name = name
        self.displayname = displayname
        self.property = propname or re.sub(r'[^\w]+', '_', self.name)
        self.matchingrule = matchingrule
        self.type = type
        self.required = required
        self.decorator = decorator
        self.is_value = is_value
        self.extras = kwargs

    def __call__(self, cls):
        setattr(cls, self.property,
            # Instantiate the specified field type
            self.type(
                name=self.name,
                displayname=self.displayname,
                decorator=self.decorator,
                matchingrule=self.matchingrule,
                is_value=self.is_value,
                **self.extras
            )
        )
        cls._fields_to_properties_[self.name] = self.property
        return cls


class EntityLinkField(EntityField):
    """Function decorator to define 'additional fields' on an Entity.

    This decorator is specifically used to define the link fields of entities.
    This is done by prepending the name with the string 'link#'

    """
    def __init__(self, name, **kwargs):
        """See EntityField.__init__()

        """
        name = 'link#%s' % name
        super(EntityLinkField, self).__init__(name=name, link=True,
                                              **kwargs)
