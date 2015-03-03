from canari.xmltools.oxml import (
    MaltegoElement,
    fields as fields_
)
from canari.maltego.message.common import (
    AdditionalField,
    Label,
    MatchingRule,
)

from canari.maltego.message.entity_field import (
    EntityField,
    EntityLinkField,
    EntityFieldType
)

class EntityElement(MaltegoElement):
    """XML Element describing an entity element.

    """
    # Strict = False

    class meta:
        tagname = 'Entity'

    # Element @Attribute's
    type = fields_.String(attrname='Type')

    # Containing elements
    fields = fields_.Dict(
        AdditionalField, key='name', tagname='AdditionalFields',
        required=False,
    )
    # Labels doesn't have any required fields, so we can't reliably store them
    # in a dict, as we could be missing field used as the key.
    labels = fields_.List(
        Label, tagname='DisplayInformation',
        required=False,
    )
    weight = fields_.Integer(
        tagname='Weight',
        required=False,
    )
    iconurl = fields_.String(
        tagname='IconURL',
        required=False,
    )
    value = fields_.String(
        tagname='Value',
        required=False,
    )


    def appendelement(self, other):
        if isinstance(other, AdditionalField):
            self.fields[other.name] = other
        elif isinstance(other, Label):
            self.labels.append(other)

    def removeelement(self, other):
        if isinstance(other, AdditionalField):
            self.fields.pop(other.name)
        elif isinstance(other, Label):
            self.labels.remove(other.name)


class MetaEntityClass(type):
    """Meta class for all entities.

    This meta class will make sure that all entity declarations will have the
    correct attributes set, if not supplied by the declaration (such as _name_,
    _type_ or _v2type_).  Even more important, a reference to the declared class
    are stored, such that one may do a reverse lookup on the type name of an
    entity and get a reference to the declared class.

    """
    _registry = {}

    def __new__(cls, clsname, bases, attrs):
        # Make sure that our class has correct/sane defaults, if not already
        # overwritten/defined in the class.
        if '_fields_to_properties_' not in attrs:
            attrs['_fields_to_properties_'] = {}
        if '_namespace_' not in attrs:
            attrs['_namespace_'] = 'maltego'
        if '_name_' not in attrs:
            attrs['_name_'] = clsname
        if '_v2type_' not in attrs:
            attrs['_v2type_'] = clsname

        # Merge the _fields_to_properties_ from all the base classes into our
        # new class instance.
        for base in bases:
            attrs['_fields_to_properties_'].update(
                base.__dict__.get('_fields_to_properties_', {})
            )

        # Create instance of the class
        new_cls = super(cls, MetaEntityClass).__new__(cls, clsname, bases, attrs)
        new_cls._type_ = '%s.%s' % (new_cls._namespace_, new_cls._name_)

        # Store a reference to the declared class, such that we may later make
        # reverse lookups from either the type or the v2type name.
        MetaEntityClass._registry[new_cls._type_] = new_cls
        MetaEntityClass._registry[new_cls._v2type_] = new_cls

        return new_cls

    @staticmethod
    def to_entity_type(entity_type_str):
        """Returns the class with the given type attribute.

        When a class is declared using this as its meta class, references to it
        are stored in an internal dict using the _type_ and _v2type_ attributes
        of the class as keys.  In other words, one may get a hold of a reference
        to a given entity class using its type or v2type name.

        """
        if entity_type_str in MetaEntityClass._registry:
            return MetaEntityClass._registry.get(entity_type_str)
        raise KeyError(
            "Error looking up entity type: '{0}'. "
            "No entity class has been declared with a _type_ or "
            "_v2type_ attribute of '{0}'. You may try to lookup "
            "the base Entity class by the key: 'None'.".format(entity_type_str)
        )



@EntityField(name='notes#', propname='notes', link=True, matchingrule=MatchingRule.Loose)
@EntityField(name='bookmark#', propname='bookmark', type=EntityFieldType.Integer, matchingrule=MatchingRule.Loose,
             link=True)
@EntityLinkField(name='maltego.link.label', propname='linklabel', matchingrule=MatchingRule.Loose)
@EntityLinkField(name='maltego.link.style', propname='linkstyle', matchingrule=MatchingRule.Loose,
                 type=EntityFieldType.Integer)
@EntityLinkField(name='maltego.link.show-label', propname='linkshowlabel', matchingrule=MatchingRule.Loose,
                 type=EntityFieldType.Enum, choices=[0, 1])
@EntityLinkField(name='maltego.link.color', propname='linkcolor', matchingrule=MatchingRule.Loose)
@EntityLinkField(name='maltego.link.thickness', propname='linkthickness', matchingrule=MatchingRule.Loose,
                 type=EntityFieldType.Integer)
class Entity(object):
    """Base class for a Maltego entity.

    This base class uses a meta class (MetaEntityClass) to configure some of the
    fundamentals when it gets declared.  All the Maltego builtin classes are
    defined in 'canari.maltego.entities'.

    """
    __metaclass__ = MetaEntityClass
    # This is a base class and should not be instantiated directly. Thus set the
    # 'special' attributes to None, which allows us to get it by making a lookup
    # in the meta class on the type name 'None", if really desired.
    _name_ = None
    _v2type_ = None
    _fields_to_properties_ = {}

    def __init__(self, value, **kwargs):
        # Store a reference to the representing XML entity element.
        if isinstance(value, EntityElement):
            self._entity = value
        else:
            self._entity = EntityElement(
                type=kwargs.pop('type', self._type_),
                value=value,
                weight=kwargs.pop('weight', None),
                iconurl=kwargs.pop('iconurl', None),
                fields=kwargs.pop('fields', None),
                labels=kwargs.pop('labels', None)
            )
        # The private field _value_property is a reference to the property that
        # are to be used as the 'value' field.  When decorating an entity class,
        # one of the @EntityField decorators may choose to be it, by specifying
        # 'is_value=True'.  This makes a mapping between the value field and
        # that field/property.
        self._value_property = None

        for p in kwargs:
            if hasattr(self, p):
                setattr(self, p, kwargs[p])


    @property
    def __fields__(self):
        return tuple(set(self._fields_to_properties_.values()))

    @property
    def __entity__(self):
        return self._entity

    @property
    def __type__(self):
        return self._type_

    def set_field(self, name, value):
        if name not in self._fields_to_properties_:
            self.appendelement(AdditionalField(name=name, value=value))
        setattr(self, self._fields_to_properties_[name], value)

    def get_field(self, name):
        if name not in self._fields_to_properties_:
            raise KeyError('No such field: %s.' % repr(name))
        return getattr(self, self._fields_to_properties_[name])

    def __getitem__(self, item):
        """Defines behavior for when an item is accessed, using the notation self[key].

        This is also part of both the mutable and immutable container
        protocols. It should raise appropriate exceptions: TypeError if the
        type of the key is wrong and KeyError if there is no corresponding value
        for the key.

        """
        if isinstance(item, basestring):
            return self.get_field(item)
        raise TypeError('Entity indices must be str, not %s' % type(item).__name__)

    def __setitem__(self, key, value):
        """Defines behavior for when an item is assigned to, using the notation
        self[key] = value.

        This is part of the mutable container protocol. Should raise
        KeyError and TypeError where appropriate.

        """
        print "__setitem__(self, key, value):", key, value
        if isinstance(key, basestring):
            print "self.set_field(key, value)"
            self.set_field(key, value)
        else:
            raise TypeError('Entity indices must be str, not %s' % type(value).__name__)

    def __getattr__(self, item):
        """Defines behaviour for when an attributes is accessed, using the notation
        self.item, on an item that doesn't exist.

        Note: It only gets called when a nonexistent attribute is accessed,
        however, so it isn't a true encapsulation solution.

        We delegate non existing attributes into the XML entity element. This
        way it becomes semi-transparent, that this entity definition is
        encapsulating the xml and other stuff.

        """
        return getattr(self._entity, item)

    def __setattr__(self, key, value):
        """Defines behaviour for when an attributes is assigned to, using the notation
        self.key = value.

        Note: Unlike __getattr__, it allows us to define behavior for assignment to
        an attribute regardless of whether or not that attribute exists.

        If the key is one of value, iconurl, weight or type, then also call
        setattr on the underlying XML entity element.

        """
        # Beware that any syntax of the form 'self.item' will result in
        # recursion as this will re-invoke the __setattr__ method.
        print "__setattr__(self, key, value):", key, value
        if key in ['value', 'iconurl', 'weight', 'type']:
            print "setattr(self._entity, key, value):"
            setattr(self._entity, key, value)
        return super(Entity, self).__setattr__(key, value)

    def __dir__(self):
        """Allow dir to also look into our encapsulated XML entity element.

        This fixes ipython and other auto completing features as well.

        """
        return sorted(set(
            self.__dict__.keys() +
            dir(Entity) +
            dir(self._entity)
        ))


    def __iadd__(self, other):
        """Addition with assignment.

        x += 1 # in other words x = x + 1

        Handles if other is a list of stuff, and calls self.appendelement on
        each element in the list. Else it just calls self.appendelement with the
        element as argument.

        """
        if isinstance(other, list):
            for o in other:
                self.appendelement(o)
        else:
            self.appendelement(other)
        return self


    def __isub__(self, other):
        """Implements subtraction with assignment.

        x -= 1 # in other words x = x - 1

        Handles if other is a list of stuff, and calls self.removeelement on
        each element in the list. Else it just calls self.removeelement with the
        element as argument.

        """
        if isinstance(other, list):
            for o in other:
                self.removeelement(o)
        else:
            self.removeelement(other)
        return self


    def __add__(self, other):
        """Implements addition.

        __iadd__ uses appendelement, which assigned from other to self.  This is
        not the intended behaviour of __add__, thus this needs to be specially
        handled in we need to implement it.

        """
        return NotImplemented


    def __sub__(self, other):
        """Implements subtraction.

        __isub__ uses removeelement, which removes other from self.  This is not
        the intended behaviour of __sub__, thus this needs to be specially
        handled in we need to implement it.

        """
        return NotImplemented

    # Pretty name for __iadd__, which handles lists of items and single items to
    # be added.
    appendelements = __iadd__

    def appendelement(self, other):
        """Adds an element into the correct collection inside this object.

        Currently you may append an AdditionalField or a Label.

        """
        print "Appendelement:", self, other

        if isinstance(other, AdditionalField):
            print "Is an AdditionalField"
            if other.name not in self._fields_to_properties_:
                # name is not in the _fields_to_properties, however since other
                # is an AdditionalField, add it to the fields anyway.  This
                # allows custom fields to be added without having a mapping
                # through an EntityField.
                self.fields[other.name] = other
            else:
                # name is in the _fields_to_properties, so it is a @EntityField
                # name. Get the property name and set the value through the
                # associated (descriptor) property (the __set__ of the
                # EngtityField type)
                propname = self._fields_to_properties_[other.name]
                setattr(self, propname, other.value)
        elif isinstance(other, Label):
            self.labels.append(other)

    # Pretty name for __isub__, which handles lists of items and single items to
    # be removed.
    removeelements = __isub__

    def removeelement(self, other):
        """Removes an element from the correct collection inside this object.

        Currently you may remove an AdditionalField or a Label.

        """
        if isinstance(other, AdditionalField) and other.name in self.fields:
            del self.fields[other.name]
        elif isinstance(other, Label) and other.name in self.labels:
            self.labels.remove(other.name)

    def __eq__(self, other):
        """Defines behavior for the equality operator, ==.

        Equality is defined in terms of the resulting XML output when rendering
        the two elements.

        """
        return self.render() == other.render()
