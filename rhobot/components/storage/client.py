"""
Module that will be used to help storage clients connect to a data store.
"""
import logging
import enum
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
    dependencies = {'xep_0050', }
    description = 'Storage Client Plugin'

    def plugin_init(self):
        self._storage_jid = None

    def post_init(self):
        self.xmpp.add_event_handler('online:store', self._store_found)
        self.xmpp.add_event_handler('offline:store', self._store_left)

    def create_payload(self):
        """
        Create a payload object for sending to the storage container.
        :return:
        """
        return StoragePayload()

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

    def create_node(self, payload, **params):
        """
        Create a new node with the provided payload
        :param payload: payload to store in the data store.
        :return: ResultCollectionPayload
        """
        storage = payload.populate_payload()
        _build_property_fields(storage, params)

        result = self.xmpp['xep_0050'].send_command(jid=self._storage_jid, node=Commands.CREATE_NODE.value,
                                                    payload=storage, flow=False)

        return ResultCollectionPayload(result['command']['form'])

    def find_nodes(self, payload, **params):
        """
        Basic search for a node.
        :param payload: StoragePayload containing a description of a node that is being searched for.
        :param params: command parameters.
        :return: ResultCollectionPayload
        """
        storage = payload.populate_payload()

        _build_property_fields(storage, params)

        result = self.xmpp['xep_0050'].send_command(jid=self._storage_jid, node=Commands.FIND_NODE.value,
                                                    payload=storage, flow=False)

        logger.info('result: %s' % result)

        return ResultCollectionPayload(result['command']['form'])

    def update_node(self, payload, **params):
        """
        Update the node described in the payload about, with the values provided.
        :param payload: payload that describes the node and the updated field values
        :param params: additional flags associated with that command.
        :return: ResultCollectionPayload.
        """
        if not payload.about:
            raise AttributeError('Missing about field in the storage payload')

        storage = payload.populate_payload()

        _build_property_fields(storage, params)

        result = self.xmpp['xep_0050'].send_command(jid=self._storage_jid, node=Commands.UPDATE_NODE.value,
                                                    payload=storage, flow=False)

        logger.info('result: %s' % result)

        return ResultCollectionPayload(result['command']['form'])

    def get_node(self, payload, **params):
        """
        Retrieve all of the details about a node from the storage provider.
        :param payload: payload containing an about for the object.
        :param params: additional properties to store in the payload.
        :return: a storage payload with all of the properties.
        """
        if not payload.about:
            raise AttributeError('Missing about field in the storage payload')

        storage = payload.populate_payload()
        _build_property_fields(storage, params)

        result = self.xmpp['xep_0050'].send_command(jid=self._storage_jid, node=Commands.GET_NODE.value,
                                                    payload=storage, flow=False)

        logger.info('result: %s' % result)

        return StoragePayload(result['command']['form'])

    def execute_cypher(self, query, **params):
        """
        Execute a cypher query and return the results to the requester.
        :param query: query string.
        :return: ResultCollectionPayload
        """
        storage = self.create_payload()
        storage.add_property(key=NEO4J.cypher, value=query)

        payload = storage.populate_payload()

        _build_property_fields(payload, params)

        result = self.xmpp['xep_0050'].send_command(jid=self._storage_jid, node=Commands.CYPHER.value,
                                                    payload=payload, flow=False)

        logger.info('result: %s' % result)

        return ResultCollectionPayload(result['command']['form'])


rho_bot_storage_client = StorageClient


def _build_property_fields(form, params):

    for key, value in params.iteritems():
        if isinstance(key, enum.Enum):
            form.add_field(var=key.value['var'], value=value, type=key.type)
        else:
            form.add_field(var=key, value=value, type='hidden')
