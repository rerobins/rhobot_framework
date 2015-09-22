"""
Unit tests for the RDF Stanza generation and manipulation.
"""
from sleekxmpp.test import SleekTest
from sleekxmpp import Message
from sleekxmpp.xmlstream import register_stanza_plugin
import sleekxmpp.plugins.xep_0004 as xep_0004
from rhobot.components.rdf_publish import RDFStanza, RDFStanzaType, RDFSourceStanza
from rhobot.components.storage import StoragePayload
from rhobot.namespace import RHO
from rdflib.namespace import FOAF, RDF


class RDFStanzaTestCase(SleekTest):

    def setUp(self):
        register_stanza_plugin(Message, RDFStanza)
        register_stanza_plugin(RDFStanza, xep_0004.Form)
        register_stanza_plugin(xep_0004.Form, xep_0004.FormField, iterable=True)
        register_stanza_plugin(xep_0004.FormField, xep_0004.FieldOption, iterable=True)
        register_stanza_plugin(RDFStanza, RDFSourceStanza)
        register_stanza_plugin(Message, xep_0004.Form)

    def test_creation(self):
        m = self.Message()
        rdf_stanza = RDFStanza(None, m)

        self.assertIsNotNone(rdf_stanza)

    def test_basic_creation(self):

        message = self.Message()

        payload = StoragePayload()
        payload.about = 'urn:rho:instance:owner'
        payload.add_type(FOAF.Person, RHO.Owner)

        rdf = RDFStanza()
        rdf['type'] = RDFStanzaType.CREATE.value
        rdf.append(payload.populate_payload())

        message.append(rdf)

        self.check(message, """
            <message>
                <rdf xmlns="urn:rho:rdf" type="create">
                    <x xmlns="jabber:x:data" type="form">
                      <field var="%s" type="text-single">
                        <value>%s</value>
                      </field>
                      <field var="%s" type="list-multi">
                        <value>%s</value>
                        <value>%s</value>
                      </field>
                    </x>
                </rdf>
            </message>
        """ % (str(RDF.about), payload.about,
               str(RDF.type), str(FOAF.Person), str(RHO.Owner), ), use_values=False)
