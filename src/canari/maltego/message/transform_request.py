from canari.xmltools.oxml import (
    MaltegoElement,
    fields as fields_
)
from canari.maltego.message.common import (
    TransformField,
)
from canari.maltego.message.entity import (
    MetaEntityClass,
    EntityElement,
    Entity,
)

class Limits(MaltegoElement):
    """XML Element describing the limits of a transform request.

    * SoftLimit: Matches the slider of the Maltego client.
    * HardLimit: ...

    These limits should be honoured by the transform!

    """
    # Strict = False

    # Element @Attribute's
    soft = fields_.Integer(attrname='SoftLimit', default=500)
    hard = fields_.Integer(attrname='HardLimit', default=10000)


class MaltegoTransformRequestMessage(MaltegoElement):
    """XML Element describing a transform request.

    The request contains the entities that are to be supplied to the transform,
    along with any transform fields and limits of how many results the user
    wants returned.

    """
    # Strict = False

    # Containing elements
    entities = fields_.List(EntityElement, tagname='Entities')
    parameters = fields_.Dict(TransformField, tagname='TransformFields',
                              key='name', required=False)
    limits = fields_.Model(Limits, required=False)

    def __init__(self, **kwargs):
        super(MaltegoTransformRequestMessage, self).__init__(**kwargs)

    @property
    def entity(self):
        if self.entities:
            entity_type = MetaEntityClass.to_entity_type(self.entities[0].type)
            return entity_type(self.entities[0])
        return Entity('')

    @property
    def params(self):
        if 'canari.local.arguments' in self.parameters:
            return self.parameters['canari.local.arguments'].value
        return self.parameters

    @property
    def value(self):
        return self.entity.value
