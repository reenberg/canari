# !/usr/bin/env python

from canari.xmltools.oxml import MaltegoElement, fields as fields_
from canari.maltego.message.common import (
    TransformField,
    AdditionalField,
    Label,
)



from canari.maltego.message.transform_discovery import *
from canari.maltego.message.transform_list import *
from canari.maltego.message.transform_request import *
from canari.maltego.message.transform_response import *
from canari.maltego.message.transform_exception import *
from canari.maltego.message.entity_field import *
from canari.maltego.message.entity import *
from canari.maltego.message.common import (
    MatchingRule
)


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.5'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'MaltegoException',
    'MaltegoTransformExceptionMessage',
    'MaltegoTransformRequestMessage',
    'Label',
    'MatchingRule',
    'AdditionalField',
    'TransformField'
    'UIMessageType',
    'UIMessage',
    'MaltegoTransformResponseMessage',
    'MaltegoMessage',
    'StringEntityField',
    'EnumEntityField',
    'IntegerEntityField',
    'BooleanEntityField',
    'FloatEntityField',
    'LongEntityField',
    'DateTimeEntityField',
    'DateEntityField',
    'timespan',
    'TimeSpanEntityField',
    'RegexEntityField',
    'ColorEntityField',
    'EntityFieldType',
    'EntityField',
    'EntityLinkField',
    'Entity',
]


class MaltegoMessage(MaltegoElement):
    # Strict = False
    message = fields_.Choice(
        fields_.Model(MaltegoTransformDiscoveryMessage), # Required = false
        fields_.Model(MaltegoTransformListMessage),      # Required = false
        fields_.Model(MaltegoTransformRequestMessage),   # Required = false
        fields_.Model(MaltegoTransformResponseMessage),  # Required = false
        fields_.Model(MaltegoTransformExceptionMessage), # Required = false
        required=False,
    )
