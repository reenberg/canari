from canari.xmltools.oxml import (
    MaltegoElement,
    fields as fields_
)

class TransformApplication(MaltegoElement):
    """XML Element describing a transform application server.

    """
    # Strict = False

    # Element @Attribute's
    registrationurl = fields_.String(
        attrname='registrationURL',
        required=False
    )
    requireapikey = fields_.Boolean(
        attrname='requireAPIKey', default=False,
        required=False
    )
    name = fields_.String(
        attrname='name', default='Unknown',
        required=False
    )
    url = fields_.String(attrname='URL')


class SeedServer(MaltegoElement):
    """XML Element describing the url of another seed server.

    """
    # Strict = False

    # Element @Attribute's
    url = fields_.String(attrname='URL')

class MaltegoTransformDiscoveryMessage(MaltegoElement):
    """XML Element describing the discovery of seed and application servers.

    The Maltego client first contacts its known discovery servers, for
    information about other seed servers and application servers.  By default
    this is the CTAS server at: https://alpine.paterva.com/CTAS31.xml

    """
    # Strict = False

    # Element @Attribute's
    source = fields_.String(attrname='source', required=False)

    # Containing elements
    other_seeds = fields_.List(
        SeedServer, tagname='OtherSeedServers',
        required=False
    )
    applications = fields_.List(
        TransformApplication, tagname='TransformApplications',
        required=True
    )



    def appendelement(self, other):
        if isinstance(other, TransformApplication):
            self.applications.append(other)
        elif isinstance(other, SeedServer):
            self.other_seeds.append(other)

    def removeelement(self, other):
        if isinstance(other, TransformApplication):
            self.applications.remove(other)
        elif isinstance(other, SeedServer):
            self.other_seeds.remove(other)
