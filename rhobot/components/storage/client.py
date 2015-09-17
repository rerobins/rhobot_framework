"""
Module that will be used to help storage clients connect to a data store.
"""
import logging

from sleekxmpp.plugins.base import base_plugin
from rhobot.components.storage.enums import Commands
from rhobot.components.storage.events import STORAGE_FOUND, STORAGE_LOST
from rhobot.components.storage.payload import StoragePayload, ResultCollectionPayload
from rhobot.components.storage.namespace import NEO4J

logger = logging.getLogger(__name__)


class StorageClient(base_plugin):
    """
    Storage client that will dump data to a storage object when one is found.

    This client should also store a journal of commands in case a data store is not present for receiving data.  Then
    when a new data storage object is present, the data will be uploaded to the storage bot.  Same thing will happen
    when there are errors during storage.  The offending command will need to be saved off.

    In addition the storage should be queued up so that the storage bot is not flooded.
    """

    name = 'rho_bot_storage_client'
    dependencies = {'xep_0050', 'rho_bot_scheduler', }
    description = 'RHO: Storage Client Plugin'

    def plugin_init(self):
        self._storage_jid = None

    def post_init(self):
        self.xmpp.add_event_handler('online:store', self._store_found)
        self.xmpp.add_event_handler('offline:store', self._store_left)

        self._scheduler = self.xmpp['rho_bot_scheduler']
        self._commands = self.xmpp['xep_0050']

    def _store_found(self, data):
        """
        When a storage container is found, update the pointer to the jid that will receive all of the data.  At some
        point it may be necessary to authenticate this data store, so that someone doesn't hijack all of the storage
        commands, but for now this will work for testing.
        :param data:
        :return:
        """
        logger.debug('Found a store: %s' % data)
        self.xmpp.event(STORAGE_FOUND)
        self._storage_jid = data

    def _store_left(self, data):
        """
        When a storage container has left, update the pointer to the jid so that data doesn't get sent to the bot
        when it's not available for storage.
        :param data:
        :return:
        """
        if self._storage_jid == data:
            self._storage_jid = None
            self.xmpp.event(STORAGE_LOST)

    def has_store(self):
        """
        Is there a storage bot associated with this client.
        :return:
        """
        return self._storage_jid is not None

    def create_node(self, payload):
        """
        Create a new node with the provided payload
        :param payload: payload to store in the data store.
        :return: ResultCollectionPayload
        """
        promise = self._scheduler.promise()

        if self.has_store():
            storage = payload.populate_payload()
            self._commands.send_command(jid=self._storage_jid, node=Commands.CREATE_NODE.value,
                                        payload=storage, flow=False,
                                        callback=self._scheduler.generate_callback_promise(promise))

            promise = promise.then(lambda s: ResultCollectionPayload(s['command']['form']))
        else:
            promise.rejected(RuntimeError('Storage node is not defined'))

        return promise

    def find_nodes(self, payload):
        """
        Basic search for a node.
        :param payload: StoragePayload containing a description of a node that is being searched for.
        :return: ResultCollectionPayload
        """
        promise = self._scheduler.promise()

        if self.has_store():
            storage = payload.populate_payload()
            self._commands.send_command(jid=self._storage_jid, node=Commands.FIND_NODE.value,
                                        payload=storage, flow=False,
                                        callback=self._scheduler.generate_callback_promise(promise))

            promise = promise.then(lambda s: ResultCollectionPayload(s['command']['form']))
        else:
            promise.rejected(RuntimeError('Storage node is not defined'))

        return promise

    def update_node(self, payload):
        """
        Update the node described in the payload about, with the values provided.
        :param payload: payload that describes the node and the updated field values
        :return: ResultCollectionPayload.
        """
        promise = self._scheduler.promise()

        if not payload.about:
            promise.rejected(AttributeError('Missing about field in the storage payload'))
        elif self.has_store():
            storage = payload.populate_payload()
            self._commands.send_command(jid=self._storage_jid, node=Commands.UPDATE_NODE.value,
                                        payload=storage, flow=False,
                                        callback=self._scheduler.generate_callback_promise(promise))
            promise = promise.then(lambda s: ResultCollectionPayload(s['command']['form']))
        else:
            promise.rejected(RuntimeError('Storage node is not defined'))

        return promise

    def get_node(self, payload):
        """
        Retrieve all of the details about a node from the storage provider.
        :param payload: payload containing an about for the object.
        :return: a storage payload with all of the properties.
        """
        promise = self._scheduler.promise()

        if not payload.about:
            promise.rejected(AttributeError('Missing about field in the storage payload'))
        elif self.has_store():
            storage = payload.populate_payload()
            self._commands.send_command(jid=self._storage_jid, node=Commands.GET_NODE.value,
                                        payload=storage, flow=False,
                                        callback=self._scheduler.generate_callback_promise(promise))
            promise = promise.then(lambda s: StoragePayload(s['command']['form']))
        else:
            promise.rejected(RuntimeError('Storage node is not defined'))

        return promise

    def execute_cypher(self, payload):
        """
        Execute a cypher query and return the results to the requester.
        :param payload: containing the query
        :return: ResultCollectionPayload
        """
        promise = self._scheduler.promise()

        if NEO4J.cypher not in payload.properties and str(NEO4J.cypher) not in payload.properties:
            promise.rejected(RuntimeError('Cypher query is not defined in the payload'))
        elif self.has_store():
            storage = payload.populate_payload()
            self._commands.send_command(jid=self._storage_jid, node=Commands.CYPHER.value,
                                        payload=storage, flow=False,
                                        callback=self._scheduler.generate_callback_promise(promise))
            promise = promise.then(lambda s: ResultCollectionPayload(s['command']['form']))
        else:
            promise.rejected(RuntimeError('Storage node is not defined'))

        return promise


rho_bot_storage_client = StorageClient
