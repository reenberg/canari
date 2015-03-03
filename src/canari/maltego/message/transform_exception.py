from canari.xmltools.oxml import (
    MaltegoElement,
    fields as fields_
)


class MaltegoException(MaltegoElement, Exception):
    """XML Element describing an exception.

    Extending the Exception class, makes it possible to raise this exception
    anywhere and have the transform runner catching it, and then returning it to
    the Maltego client.

    """
    # Strict = False

    class meta:
        tagname = 'Exception'

    def __init__(self, value):
        super(MaltegoException, self).__init__(value=value),

    # Element @Attribute's
    # Error codes used for default (built in) error messages.
    code = fields_.Integer(attrname='code', required=False)
    # Element @Text value
    value = fields_.String(tagname='.')



class MaltegoTransformExceptionMessage(MaltegoElement):
    """XML Element describing the exceptions that occurred.

    """
    # Strict = False

    # Containing elements
    exceptions = fields_.List(MaltegoException, tagname='Exceptions',
                              required=False)

    def appendelement(self, exception):
        if isinstance(exception, MaltegoException):
            self.exceptions.append(exception)
        else:
            self.exceptions.append(MaltegoException(str(exception)))
