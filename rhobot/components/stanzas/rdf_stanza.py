from enum import Enum
from sleekxmpp.xmlstream import ElementBase


XMLNS = 'urn:rho:rdf'


class RDFStanzaType(Enum):
    REQUEST = 'request'
    RESPONSE = 'response'
    CREATE = 'create'
    UPDATE = 'update'
    SEARCH_REQUEST = 'search'
    SEARCH_RESPONSE = 'search_response'


class RDFStanza(ElementBase):
    """
    Stanza responsible for requesting and responding to rdf requests.
    <rdf xmlns='rho:rdf' type='request|response'>
        <x xmlns='data'... />
    </rdf>

    source provides a command that can be used to search for other valid details.
    """
    name = 'rdf'
    namespace = XMLNS
    plugin_attrib = 'rdf'
    interfaces = {'type', }


class RDFSourceStanza(ElementBase):
    """
    Stanza responsible for providing details about the source of the data that is coming in.
    """
    name = 'source'
    namespace = XMLNS
    plugin_attrib = 'source'
    interfaces = {'name', 'command', }
