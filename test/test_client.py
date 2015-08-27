import unittest
import mock
from rhobot.components.storage.client import rho_bot_storage_client
from rhobot.components.storage import StoragePayload, ResultCollectionPayload, ResultPayload
from rhobot.components.storage.enums import Commands
from rhobot.namespace import RHO
from rdflib.namespace import FOAF, RDF, RDFS


class ClientTestCase(unittest.TestCase):

    def test_storage_found(self):

        client = rho_bot_storage_client(xmpp=mock.MagicMock(), config=None)
        client.plugin_init()

        self.assertFalse(client.has_store())

        storage_client = 'rhobot@conference.localhost/neo4j'

        client._store_found(storage_client)

        self.assertTrue(client.has_store())
        self.assertEqual(client._storage_jid, storage_client)

        client._store_left('rhobot@conference.localhost/other_storage')

        self.assertTrue(client.has_store())
        self.assertEqual(client._storage_jid, storage_client)

        client._store_left(storage_client)

        self.assertFalse(client.has_store())

    def test_find_node(self):

        about = 'urn:rho:owner_uri'
        types = [str(FOAF.Person), str(RHO.Owner)]

        result = ResultCollectionPayload()
        result.append(ResultPayload(about=about, types=types))
        result = dict(command=dict(form=result.populate_payload()))

        command_mock = mock.MagicMock()
        command_mock.configure_mock(**{'send_command.return_value': result})

        xmpp_mock = mock.MagicMock()
        xmpp_mock.configure_mock(**{'__getitem__.return_value': command_mock})

        xmpp_mock['xep_0050'] = command_mock

        client = rho_bot_storage_client(xmpp=xmpp_mock)
        client.plugin_init()

        storage_client = 'rhobot@conference.localhost/neo4j'
        client._store_found(storage_client)

        payload = StoragePayload()
        payload.about = about
        payload.add_type(*types)

        result = client.find_nodes(payload=payload)

        self.assertEqual(1, command_mock.send_command.call_count)

        args, kwargs = command_mock.send_command.call_args

        self.assertIn('jid', kwargs)
        self.assertEqual(storage_client, kwargs['jid'])

        self.assertIn('payload', kwargs)
        sent_payload = kwargs['payload']

        fields = sent_payload.get_fields()

        self.assertIsNotNone(fields.get(str(RDF.about), None))
        about_field = fields.get(str(RDF.about))
        self.assertEqual(about_field.get_value(), about)

        types_field = fields.get(str(RDF.type), None)
        self.assertIsNotNone(types_field)
        self.assertEqual(types_field.get_value(), types)

        self.assertIn('node', kwargs)
        self.assertEqual(kwargs['node'], Commands.FIND_NODE.value)
