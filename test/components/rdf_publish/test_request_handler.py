"""
Send out a single request and handle it correctly.
"""
import unittest
import mock
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.plugins.xep_0004 import Form, FormField, FieldOption
from sleekxmpp import Message
from rhobot.components.rdf_publish import rho_bot_rdf_publish, RDFStanzaType
from rhobot.components.storage import StoragePayload, ResultCollectionPayload, ResultPayload
from rdflib.namespace import FOAF, RDF, RDFS
from rhobot.namespace import RHO


class ResponseTestCase(unittest.TestCase):

    def setUp(self):
        self.scheduler_plugin = mock.MagicMock()
        self.roster_plugin = mock.MagicMock(**{'get_jid.return_value': 'rhobot@conference.local/bot'})

        plugins = {'rho_bot_scheduler': self.scheduler_plugin,
                   'rho_bot_roster': self.roster_plugin}

        def getitem(name):
            return plugins.get(name, False)

        self.xmpp = mock.MagicMock(**{'name': 'test bot'})
        self.xmpp.__getitem__.side_effect = getitem

        self.rdf_publisher = rho_bot_rdf_publish(self.xmpp, None)
        self.rdf_publisher.plugin_init()
        self.rdf_publisher.post_init()
        self.xmpp = mock.MagicMock

        register_stanza_plugin(FormField, FieldOption, iterable=True)
        register_stanza_plugin(Form, FormField, iterable=True)

    def test_empty_handle_request(self):

        payload = StoragePayload()
        payload.add_type(FOAF.Person, RHO.Owner)

        self.rdf_publisher.send_out_request(payload)

        # Verify the payload request.
        self.assertEqual(1, self.roster_plugin.send_message.call_count)

        args, kwargs = self.roster_plugin.send_message.call_args
        payload = kwargs['payload']

        message = Message()
        message.append(payload)
        message['thread'] = kwargs['thread_id']

        # Test empty request.
        self.rdf_publisher._receive_message(message)

    def test_no_result(self):
        payload = StoragePayload()
        payload.add_type(FOAF.Person, RHO.Owner)

        self.rdf_publisher.send_out_request(payload)

        # Verify the payload request.
        self.assertEqual(1, self.roster_plugin.send_message.call_count)

        args, kwargs = self.roster_plugin.send_message.call_args
        payload = kwargs['payload']

        message = Message()
        message.append(payload)
        message['thread'] = kwargs['thread_id']

        handler_mock = mock.Mock(return_value=None)
        self.rdf_publisher.add_request_handler(handler_mock)

        self.rdf_publisher._receive_message(message)
