from enum import Enum
from sleekxmpp.xmlstream import ElementBase


class RDFStanzaType(Enum):
    REQUEST = 'request'
    RESPONSE = 'response'
    CREATE = 'create'
    UPDATE = 'update'
    SEARCH_REQUEST = 'search'
    SEARCH_RESPONSE = 'search_response'

class RDFType(ElementBase):
    """
    Stanza that will allow for typing information to be placed in the form field.
    """
    name = 'rdftype'
    namespace = 'rho:rdf'
    plugin_attrib = 'rdftype'
    interfaces = {'type', }


class RDFStanza(ElementBase):
    """
    Stanza responsible for requesting and responding to rdf requests.
    <rdf xmlns='rho:rdf' type='request|response'>
        <x xmlns='data'... />
        <source>
            <name>Some Name</name>
            <command>xmpp:jid@jiddomain.com?command;node=some_node;action=execute</command>
        </source>
    </rdf>

    source provides a command that can be used to search for other valid details.
    """
    name = 'rdf'
    namespace = 'rho:rdf'
    plugin_attrib = 'rdf'
    interfaces = {'type', }


class RDFSourceStanza(ElementBase):
    """
    Stanza responsible for providing details about the source of the data that is coming in.
    """
    name = 'source'
    namespace = 'rdf:rho'
    plugin_attrib = 'source'
    interfaces = {'name', 'command', }
