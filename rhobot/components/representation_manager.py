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

    def _start(self, event):
        create = True
        payload = StoragePayload()
        payload.add_type(FOAF.Agent, RDFS.Resource)
        payload.add_property(RDFS.seeAlso, self.xmpp.get_uri())

        result = self.xmpp['rho_bot_storage_client'].find_nodes(payload)

        if result.results:
            self._node_id = result.results[0].about
            create = False

        update_payload = StoragePayload()
        update_payload.add_type(FOAF.Agent, RDFS.Resource)
        update_payload.add_property(RDFS.seeAlso, self.xmpp.get_uri())
        update_payload.add_property(FOAF.name, self.xmpp.name)

        if self._node_id:
            update_payload.about = self._node_id
            storage_result = self.xmpp['rho_bot_storage_client'].update_node(update_payload)
        else:
            storage_result = self.xmpp['rho_bot_storage_client'].create_node(update_payload)

        publish_payload = StoragePayload()
        publish_payload.about = storage_result.results[0].about
        publish_payload.add_type(storage_result.results[0].types)

        if create:
            self.xmpp['rho_bot_rdf_publish'].publish_create(publish_payload)
        else:
            self.xmpp['rho_bot_rdf_publish'].publish_update(publish_payload)


rho_bot_representation_manager = RepresentationManager
