"""
Module that will be used to help storage clients connect to a data store.
"""
import logging
import enum
from rdflib.namespace import RDFS, RDF
from sleekxmpp.plugins.base import base_plugin
from rhobot.components.storage.enums import Commands
from rhobot.components.storage.events import STORAGE_FOUND, STORAGE_LOST

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
        self._unpack_payload()

    def add_type(self, *args):
        """
        Add a list of types to the container.
        :param args:
        :return:
        """
        for arg in args:
            self._types.append(str(arg))

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

        self._properties[key] += value

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

    def _populate_payload(self):
        """
        Translates the contents of this object into a payload for sending across to the storage entity.
        :return: the populated form
        """
        self._container.clear()

        if self.about:
            self._container.add_field(var=str(RDF.about), value=[self.about], ftype=str(RDFS.Literal))

        if len(self._types):
            self._container.add_field(var=str(RDF.type), value=self._types, ftype=str(RDF.type))

        for key, value in self._properties.iteritems():
            self._container.add_field(var=str(key), value=value, ftype=str(RDFS.Literal))

        for key, value in self._references.iteritems():
            self._container.add_field(var=str(key), value=value, ftype=str(RDFS.Resource))

        return self._container

    def _unpack_payload(self):
        """
        Unpack the current container to class variables.
        """
        self.about = None
        self._types = []
        self._properties = {}
        self._references = {}

        for key, value in self._container.field.iteritems():
            if key == str(RDF.about):
                self.about = value.get_value()[0]
            elif value['type'] == str(RDF.type):
                self._types = value.get_value()
            elif value['type'] == str(RDFS.Literal):
                self._properties[key] = value.get_value()
            elif value['type'] == str(RDFS.Resource):
                self._references[key] = value.get_value()

    def types(self):
        return self._types

    def properties(self):
        return self._properties

    def references(self):
        return self._references


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
        :return:
        """
        storage = payload._populate_payload()

        result = self.xmpp['xep_0050'].send_command(jid=self._storage_jid, node=Commands.CREATE_NODE.value,
                                                    payload=storage, flow=False)

        # This command will return the URI of the node that was inserted into the database.
        uri = result['command']['form'].get_items()[0][str(RDF.about)]

        return uri

    def find_nodes(self, payload, **params):
        storage = payload._populate_payload()

        _build_property_fields(storage, params)

        result = self.xmpp['xep_0050'].send_command(jid=self._storage_jid, node=Commands.FIND_NODE.value,
                                                    payload=storage, flow=False)

        logger.info('result: %s' % result)

        return result

    def update_node(self, payload, **params):

        storage = payload._populate_payload()

        _build_property_fields(storage, params)

        result = self.xmpp['xep_0050'].send_command(jid=self._storage_jid, node=Commands.UPDATE_NODE.value,
                                                    payload=storage, flow=False)

        logger.info('result: %s' % result)

        return result


rho_bot_storage_client = StorageClient

def _build_property_fields(form, params):

    for key, value in params.iteritems():
        if isinstance(key, enum.Enum):
            form.add_field(var=key.value['var'], value=value, type=key.type)
        else:
            form.add_field(var=key, value=value, type='hidden')
