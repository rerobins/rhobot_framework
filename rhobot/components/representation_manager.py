"""
Manages the representation RDF node for this bot.
"""
import logging

from sleekxmpp.plugins.base import base_plugin
from rhobot.components.storage.events import STORAGE_FOUND
from rhobot.components.storage import StoragePayload
from rdflib.namespace import RDFS, FOAF
from rhobot.stanza_modification import patch_form_fields;

patch_form_fields()

logger = logging.getLogger(__name__)


class RepresentationManager(base_plugin):
    """
    Service that will send out requests and farm out the incoming messages to the appropriate handlers.
    """

    name = 'rho_bot_representation_manager'
    dependencies = {'rho_bot_storage_client', 'rho_bot_rdf_publish', }
    description = 'Representation Manager'

    def plugin_init(self):
        """
        Configure the plugin to handle the private storage of data.
        :return:
        """
        self.xmpp.add_event_handler(STORAGE_FOUND, self._start)
        self._node_id = None

    def post_init(self):
        self._storage_client = self.xmpp['rho_bot_storage_client']
        self._rdf_publish = self.xmpp['rho_bot_rdf_publish']

    @property
    def representation_uri(self):
        return self._node_id

    def _start(self, event):
        payload = StoragePayload()
        payload.add_type(FOAF.Agent, RDFS.Resource)
        payload.add_property(RDFS.seeAlso, self.xmpp.get_uri())

        promise = self._storage_client.find_nodes(payload)

        node_found_promise = promise.then(self._node_found)

        node_found_promise.then(self._update_node, self._create_node)

    def _node_found(self, result):
        """
        Determine if the node that represents this bot is found on the server.
        :param result: result from find nodes command.
        :return:
        """
        if result.results:
            node_id = result.results[0].about
            return node_id

        raise RuntimeError('Not Found')

    def _update_node(self, node_identifier):
        """
        Update the node that was found, and then publish the update.
        :param node_identifier: identifier of the node to update.
        :return:
        """
        payload = self._create_payload()
        payload.about = node_identifier

        promise = self._storage_client.update_node(payload).then(self._publish_update)

        return promise

    def _create_node(self, error_message):
        payload = self._create_payload()

        promise = self._storage_client.create_node(payload).then(self._publish_create)

        return promise

    def _create_payload(self):

        update_payload = StoragePayload()
        update_payload.add_type(FOAF.Agent, RDFS.Resource)
        update_payload.add_property(RDFS.seeAlso, self.xmpp.get_uri())
        update_payload.add_property(FOAF.name, self.xmpp.name)

        return update_payload

    def _publish_update(self, storage_result):

        publish_payload = StoragePayload()
        publish_payload.about = storage_result.results[0].about
        publish_payload.add_type(*storage_result.results[0].types)

        self._node_id = publish_payload.about

        self._rdf_publish.publish_update(publish_payload)

    def _publish_create(self, storage_result):

        publish_payload = StoragePayload()
        publish_payload.about = storage_result.results[0].about
        publish_payload.add_type(*storage_result.results[0].types)

        self._node_id = publish_payload.about

        self._rdf_publish.publish_create(publish_payload)


rho_bot_representation_manager = RepresentationManager
