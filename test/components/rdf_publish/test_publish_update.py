"""
Publish update and handle the returning of a response.
"""
import unittest
import mock
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.plugins.xep_0004 import Form, FormField, FieldOption
from sleekxmpp import Message
from rhobot.components.rdf_publish import rho_bot_rdf_publish, RDFStanzaType
from rhobot.components.storage import StoragePayload
from rdflib.namespace import FOAF, RDF, RDFS
from rhobot.namespace import RHO
import time


class PublishUpdateTestCase(unittest.TestCase):

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

    def test_publish_update(self):

        publish_urn = 'rho:instances.owner'

        payload = StoragePayload()
        payload.add_type(FOAF.Person, RHO.Owner)
        payload.about = publish_urn

        self.rdf_publisher.publish_update(payload)

        self.assertEqual(1, self.roster_plugin.send_message.call_count)

        args, kwargs = self.roster_plugin.send_message.call_args

        self.assertIn('thread_id', kwargs)
        self.assertIn('payload', kwargs)

        self.assertIsNone(kwargs['thread_id'])
        self.assertIsNotNone(kwargs['payload'])

        payload = kwargs['payload']

        self.assertEqual(payload['type'], RDFStanzaType.UPDATE.value)

        form = payload['form']

        self.assertIsNotNone(form.get_fields()[str(RDF.type)])
        values = form.get_fields()[str(RDF.type)].get_value()
        self.assertIn(str(FOAF.Person), values)
        self.assertIn(str(RHO.Owner), values)

        self.assertIsNotNone(form.get_fields()[str(RDF.about)])
        values = form.get_fields()[str(RDF.about)].get_value()
        self.assertEqual(publish_urn, values)

    def test_update_handler(self):

        publish_urn = 'rho:instances.owner'

        payload = StoragePayload()
        payload.add_type(FOAF.Person, RHO.Owner)
        payload.about = publish_urn

        self.rdf_publisher.publish_update(payload)
        args, kwargs = self.roster_plugin.send_message.call_args

        payload = kwargs['payload']

        message = Message()
        message.append(payload)

        self.rdf_publisher._receive_message(message)

        create_handler = mock.MagicMock()
        self.rdf_publisher.add_update_handler(create_handler)

        self.rdf_publisher._receive_message(message)
        self.assertEqual(self.scheduler_plugin.defer.call_args[0][0], create_handler)
        self.assertEqual(str(self.scheduler_plugin.defer.call_args[0][1]), str(message['rdf']))
