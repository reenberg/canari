from canari.xmltools.oxml import (
    MaltegoElement,
    fields as fields_
)

##
## Misc stuff used by the messaging classes
##

class MatchingRule(object):
    """Matching rules for comparison.

    Typically controls how an item of an element (e.g., a field of en entity)
    influences equality of two elements. Two elements would be treated as equal
    if all their strict items are equal, and the two elements would then
    normally get merged.

    """
    Strict = "strict"
    Loose = "loose"

class TransformField(MaltegoElement):
    """Input fields used in a transform request message.

    """
    # Strict = False

    class meta:
        tagname = 'Field'

    def __init__(self, name=None, value=None, **kwargs):
        super(TransformField, self).__init__(name=name, value=value, **kwargs)

    # Element @Attribute's
    name = fields_.String(attrname='Name')

    # Element @Text value
    value = fields_.String(tagname='.')

class AdditionalField(MaltegoElement):
    """XML Element describing the (additional) field of an entity.

    Encapsulated in the various entity field types:
    * String (StringEntityField)
    * Integer (IntegerEntityField)
    * Long (LongEntityField)
    * Float (FloatEntityField)
    * Bool (BooleanEntityField)
    * Enum (EnumEntityField)
    * Date (DateEntityField)
    * DateTime (DateTimeEntityField)
    * TimeSpan (TimeSpanEntityField)
    * Color (ColorEntityField)

    and used by decorating an entity with the EntityField decorator class, which
    takes an entity field type as one of its arguments.

    """
    # Strict = False

    class meta:
        tagname = 'Field'

    # Element @Attribute's
    name = fields_.String(attrname='Name')
    displayname = fields_.String(
        attrname='DisplayName',
        required=False
    )
    matchingrule = fields_.String(
        attrname='MatchingRule', default=MatchingRule.Strict,
        required=False
    )

    # Element @Text value
    value = fields_.String(tagname='.', required=False)


class Label(MaltegoElement):
    """XML Element describing the display information of an entity.

    """
    # Strict = False

    def __init__(self, name=None, value=None, **kwargs):
        super(Label, self).__init__(name=name, value=value, **kwargs)

    # Element @Attribute's
    type = fields_.String(
        attrname='Type', default='text/text',
        required=False,
    )
    name = fields_.String(
        attrname='Name',
        required=False,
    )

    # Element @Text value
    value = fields_.CDATA(
        tagname='.',
        required=False,
    )
