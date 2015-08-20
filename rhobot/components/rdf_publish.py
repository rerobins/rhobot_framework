"""
Plugin that is responsible for publishing requests or responses to rdf messages in the channel.  Since IQ messages
cannot be broadcast to all of the members of a channel, this functionality will piggy back on messages instead.
"""

from sleekxmpp.plugins.base import base_plugin
from sleekxmpp.xmlstream import ElementBase, register_stanza_plugin
from sleekxmpp.plugins.xep_0004.stanza.form import Form
from sleekxmpp import Message
from rhobot.components.roster import RosterComponent
from rdflib.namespace import FOAF
import logging
import uuid

logger = logging.getLogger(__name__)


class RDFStanza(ElementBase):
    """
    Stanza responsible for requesting and responding to rdf requests.
    <rdf xmlns='rho:rdf' type='request|response'>
        <x xmlns='data'
    </rdf>
    """
    name = 'rdf'
    namespace = 'rho:rdf'
    plugin_attrib = 'rdf'
    interfaces = {'command', }


class RDFPublish(base_plugin):

    name = 'rho_bot_rdf_publish'
    dependencies = {'rho_bot_storage_client', 'rho_bot_roster', 'rho_bot_scheduler', }
    description = 'Configuration Plugin'

    def plugin_init(self):
        register_stanza_plugin(Message, RDFStanza)
        register_stanza_plugin(RDFStanza, Form)

        self.xmpp.add_event_handler(RosterComponent.CHANNEL_JOINED, self._channel_joined)
        self.xmpp['rho_bot_scheduler'].schedule_task(self._send_out_request, 3.0, repeat=True)

    def _channel_joined(self, event):
        logger.info('Joined the registration channel')
        self.xmpp['rho_bot_roster'].add_message_received_listener(self._receive_request_message)

    def _send_out_request(self):
        logger.info('Sending out request for rho::owner')

        payload = self.xmpp['rho_bot_storage_client'].create_payload()
        payload.add_type(FOAF.Person, 'rho::owner')

        rdf_stanza = RDFStanza()
        rdf_stanza['command'] = 'request'
        rdf_stanza.append(payload._populate_payload())

        self.xmpp['rho_bot_roster'].send_message(payload=rdf_stanza, payload_name='rdf', thread_id=str(uuid.uuid4()))

    def _receive_request_message(self, message):
        logger.info('Received a request message: %s' % message)



rho_bot_rdf_publish = RDFPublish