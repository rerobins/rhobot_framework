import unittest

import mock
from rhobot.components.storage.client import rho_bot_storage_client


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

