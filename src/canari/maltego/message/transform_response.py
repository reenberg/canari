from canari.xmltools.oxml import (
    MaltegoElement,
    fields as fields_
)
from canari.maltego.message.entity import (
    EntityElement,
    Entity
)

class UIMessageType:
    Fatal = "FatalError"
    Partial = "PartialError"
    Inform = "Inform"
    Debug = "Debug"


class UIMessage(MaltegoElement):
    """XML Element describing a notification/message.

    This is displayed to the user in the Maltego client.

    """
    # Strict = False

    def __init__(self, value=None, **kwargs):
        super(UIMessage, self).__init__(value=value, **kwargs)

    # Element @Attribute's
    type = fields_.String(attrname='MessageType', default=UIMessageType.Inform)
    # Element @Text value
    value = fields_.String(tagname='.')


class MaltegoTransformResponseMessage(MaltegoElement):
    """XML Element describing a transform response/result.

    The response/result contains a list of entities and possibly a list of UI
    messages/notifications.

    """
    # Strict = False

    # Containing elements
    entities = fields_.List(EntityElement, tagname='Entities')
    uimessages = fields_.List(
        UIMessage, tagname='UIMessages',
        required=False,
    )


    def appendelement(self, other):
        if isinstance(other, Entity):
            self.entities.append(other.__entity__)
        elif isinstance(other, EntityElement):
            self.entities.append(other)
        elif isinstance(other, UIMessage):
            self.uimessages.append(other)

    def removeelement(self, other):
        if isinstance(other, Entity):
            self.entities.remove(other.__entity__)
        elif isinstance(other, EntityElement):
            self.entities.remove(other)
        elif isinstance(other, UIMessage):
            self.uimessages.remove(other)
