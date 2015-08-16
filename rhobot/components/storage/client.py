"""
Module that will be used to help storage clients connect to a data store.
"""
import logging
from rdflib.namespace import RDFS, RDF
from sleekxmpp.plugins.base import base_plugin
from rhobot.components.storage.enums import Commands

logger = logging.getLogger(__name__)


class StoragePayload:
    """
    Payload object that will contain the workspace for the data to be stored or looked up in the database.
    """

    def __init__(self, _container):
        self._container = _container
        self.about = None
        self._types = []
        self._properties = {}
        self._references = {}

    def add_type(self, *args):
        """
        Add a list of types to the container.
        :param args:
        :return:
        """
        self._types += args

    def add_property(self, key, value):
        """
        Add a property to the list of values for storage.
        :param key:
        :param value: should be a list, otherwise will be converted to a list.
        :return:
        """
        if key not in self._properties:
            self._properties[key] = []

        if not isinstance(value, list):
            value = [value]

        self._properties += value

    def add_reference(self, key, value):
        """
        Add a reference to the list of values for storage.
        :param key:
        :param value: should be a list, otherwise will be converted to a list.
        :return:
        """
        if key not in self._references:
            self._references[key] = []

        if not isinstance(value, list):
            value = [value]

        self._references[key] = value

    def __populate_payload(self):
        """
        Translates the contents of this object into a payload for sending across to the storage entity.
        :return: the populated form
        """
        if self.about:
            self._container.add_field(var=str(RDF.about), value=[self.about], ftype=str(RDFS.Literal))

        if len(self._types):
            self._container.add_field(var=str(RDF.type), value=self._types, ftype=str(RDFS.type))

        for key, value in self._properties.iteritems():
            self._container.add_field(var=str(key), value=value, ftype=str(RDFS.Literal))

        for key, value in self._references.iteritems():
            self._container.add_field(var=str(key), value=value, ftype=str(RDFS.Resource))

        return self._container


class StorageClient(base_plugin):
    """
    Storage client that will dump data to a storage object when one is found.

    This client should also store a journal of commands in case a data store is not present for receiving data.  Then
    when a new data storage object is present, the data will be uploaded to the storage bot.  Same thing will happen
    when there are errors during storage.  The offending command will need to be saved off.

    In addition the storage should be queued up so that the storage bot is not flooded.
    """

    name = 'rho_bot_storage_client'
    dependencies = {'rho_bot_roster', 'xep_0050'}
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
        return StoragePayload(self.xmpp['xep_0004'].make_form(ftype='result'))

    def _store_found(self, data):
        """
        When a storage container is found, update the pointer to the jid that will receive all of the data.  At some
        point it may be necessary to authenticate this data store, so that someone doesn't hijack all of the storage
        commands, but for now this will work for testing.
        :param data:
        :return:
        """
        logger.info('Found a store: %s' % data)
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

    def create_node(self, payload):
        """
        Create a new node with the provided payload
        :param payload: payload to store in the data store.
        :return:
        """
        storage = payload.__populate_payload()

        session = dict(next=self._store_result,
                       error=self._store_error,
                       payload=[storage])

        self.xmpp['xep_0050'].start_command(jid=self._storage_jid, node=Commands.CREATE_NODE.value, session=session)

    def _store_result(self, iq, session):
        logger.info('Store Result iq: %s' % iq)
        logger.info('Store Result session: %s' % session)

    def _store_error(self, iq, session):
        logger.info('Store Error iq: %s' % iq)
        logger.info('Store Error session: %s' % session)

rho_bot_storage_client = StorageClient
