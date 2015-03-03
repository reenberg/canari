from canari.xmltools.oxml import (
    MaltegoElement,
    fields as fields_
)


class Input(MaltegoElement):
    """Elements for UIInputRequirements

    Input of type 'string' with an empty or non-existing defaultvalue will act
    as a popup, when they are non-optional.

    """

    name = fields_.String(attrname='Name')
    type = fields_.String(attrname='Type') # 'int' or 'string'
    display = fields_.String(attrname='Display')
    defaultvalue = fields_.String(attrname='DefaultValue', required=False)
    optional = fields_.Boolean(attrname='Optional', default=False)

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.type = kwargs['type']
        self.display = kwargs['display']

        attr = kwargs.get('defaultvalue', None)
        if attr is not None: self.defaultvalue = attr

        attr = kwargs.get('optional', None)
        if attr is not None: self.optional = attr


class Transform(MaltegoElement):
    owner = fields_.String(attrname='owner')
    author = fields_.String(attrname='Author')
    version = fields_.String(attrname='Version') # Required field though Paterva TDS lists it as optional
    maxinput = fields_.Integer(attrname='MaxEntityInputCount')
    maxoutput = fields_.Integer(attrname='MaxEntityOutputCount')
    locationrelevance = fields_.String(attrname='LocationRelevance')
    description = fields_.String(attrname='Description', required=False)
    disclaimer = fields_.String(attrname='Disclaimer', required=False)
    displayname = fields_.String(attrname='UIDisplayName')
    transformname = fields_.String(attrname='TransformName')
    inputrequirements = fields_.List(Input, tagname='UIInputRequirements')
    outputentities = fields_.List(fields_.String(tagname='OutputEntity'),
                                  tagname='OutputEntities')
    inputentity = fields_.String(tagname='InputEntity')

    def __init__(self, transform=None, **kwargs):
        if transform:
            # - Mandatory fields have no error handling.
            # - Optional fields test whether the attribute exists.

            self.owner = transform.dotransform.owner
            self.author = transform.__author__ # TODO: Add maintainer info and email.
            self.version = transform.__version__
            self.maxinput = 0
            self.maxoutput = 0
            self.locationrelevance = 'global'
            self.displayname = transform.dotransform.label

            attr = getattr(transform.dotransform, 'description', None)
            if attr is not None: self.description = attr

            attr = getattr(transform.dotransform, 'disclaimer', None)
            if attr is not None: self.disclaimer = attr

            self.transformname = transform.dotransform.uuids[0] # TODO: Handle multiple input methods.
            self.inputentity = transform.dotransform.inputs[0][1].__name__ # TODO: FIX
            self.outputentities = getattr(transform.dotransform, 'outputentities', ['Any'])

            attr = getattr(transform.dotransform, 'inputrequirements', None)
            if attr is not None:
                for elem in attr: self.appendelement(Input(**elem))


        super(Transform, self).__init__(**kwargs)

    def appendelement(self, other):
        if isinstance(other, Input):
            self.inputrequirements.append(other)

    def removeelement(self, other):
        if isinstance(other, Input):
            self.inputrequirements.remove(other)


class OAuthAuthenticator(MaltegoElement):
    """OAuth v1.0a and v2.0 implementation.

    The Maltego client implement v1.0a and v2.0 of the OAuth model through the
    scribe-java package (https://github.com/fernandezpablo85/scribe-java).  The
    default Paterva servers shows a demo of how to use v1.0a against Twitter.

    NOTE: There are some specific behaviour for the different OAuth versions:

    - v1.0a:
        * The authorization url will replace the following placeholder:
            * {token}: ....


    - v2.0:
        * The authorization url will replace the following placeholders:
            * {apiKey}: ...
            * {callback}: ...



    v2.0
    String str = OAuthModel.this._authenticator.getAuthorizationUrl();
    str = str.replace("{apiKey}", paramAnonymousOAuthConfig.getApiKey());
    str = str.replace("{callback}", OAuthEncoder.encode(paramAnonymousOAuthConfig.getCallback()));

    """
    # Strict = False

    class OAuthVersion(MaltegoElement):

        value = fields_.String(tagname=".")

        def __init__(self, version):
            self.value = version

    # Static instances of the supported versions. Needs to be defined this way
    # due to python scoping 'quirks'.  The class must be defined before we can
    # reference it.
    OAuthVersion.V1a = OAuthVersion("1.0a")
    OAuthVersion.V2 = OAuthVersion("2.0")


    # Element @Attribute's
    name = fields_.String(attrname='Name')
    displayname = fields_.String(attrname='DisplayName')


    # Containing elements
    description = fields_.String(
        tagname='Description',
        required=False,
    )
    version = fields_.Model(OAuthVersion)
    callbackport = fields_.Integer(
        tagname='CallbackPort',
        required=False,
    )
    accesstokenendpoint = fields_.String(
        tagname='AccessTokenEndpoint'
    )
    requesttokenendpoint = fields_.String(
        tagname='RequestTokenEndpoint',
        required=False
    )
    # Note that for v1.0a the url may contain the placeholder {token} and for
    # v2.0 it may contain the placeholders {apiKey} and {callback}.
    authorizationurl = fields_.String(
        tagname='AuthorizationUrl'
    )
    appkey = fields_.String(tagname='AppKey')
    appsecret = fields_.String(tagname='AppSecret')
    icon = fields_.String(tagname='Icon')
    accesstokeninput = fields_.String(
        tagname='AccessTokenInput'
    )
    accesstokenpublickey = fields_.String(
        tagname='AccessTokenPublicKey'
    )



class Authenticators(MaltegoElement):
    """Lists of the various authenticators

    """

    # Containing elements
    oauth = fields_.List(
        OAuthAuthenticator, tagname='OAuthAuthenticators',
        required=False
    )

    def appendelement(self, other):
        if isinstance(other, OAuthAuthenticator):
            self.oauth.append(other)

    def removeelement(self, other):
        if isinstance(other, OAuthAuthenticator):
            self.oauth.remove(other)


class MaltegoTransformListMessage(MaltegoElement):
    # Strict = False

    # Containing elements
    transforms = fields_.List(
        Transform, tagname='Transforms',
        required=False
    )

    authenticators = fields_.Model(Authenticators,
        required=False
    )

    def appendelement(self, other):
        if isinstance(other, Transform):
            self.transforms.append(other)

    def removeelement(self, other):
        if isinstance(other, Transform):
            self.transforms.remove(other)
