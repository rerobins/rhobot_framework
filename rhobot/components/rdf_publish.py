"""
Plugin that is responsible for publishing requests or responses to rdf messages in the channel.  Since IQ messages
cannot be broadcast to all of the members of a channel, this functionality will piggy back on messages instead.

Need to figure out how to handle all of the methods associated with the functionality.

For the response to a message it can be easily done by executing the command in a blocking thread and then respond to
it.

The problem is how to get information when this bot is the one requesting the information.  Because I want to block
processing of the thread that is making the request.  I really want the functionality here to block like an iq message
does in the sleekxmpp framework.



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

        self._pending_requests = dict()
        self._handlers = []

    def _channel_joined(self, event):
        """
        When the channel is joined, add a message listener for all of the incoming requests and the responses that are
        made to requests made by this bot.
        :param event: ignored.
        :return: None
        """
        logger.info('Joined the registration channel')
        self.xmpp['rho_bot_roster'].add_message_received_listener(self._receive_request_message)

    def send_out_request(self, payload, callback, timeout=10.0):
        """
        Send out an rdf request for the provided payload.
        :param payload: the payload to serialize and then
        :param callback: call back to notify when the results come in.  Callback will be provided with one of two
        parameters, payload, or timeout (bool).  If the timeout is true, then there should be no payload, otherwise
        payload should be not None.
        :param timeout: the timeout that will be used to cancel the request.
        :return:
        """
        rdf_stanza = RDFStanza()
        rdf_stanza['command'] = 'request'
        rdf_stanza.append(payload._populate_payload())

        thread_identifier = str(uuid.uuid4())

        self._pending_requests[thread_identifier] = callback

        self.xmpp['rho_bot_roster'].send_message(payload=rdf_stanza, thread_id=thread_identifier)

        self.xmpp['rho_bot_scheduler'].schedule_event(callback=self._generate_cancel_event(callback, thread_identifier),
                                                      delay=timeout)

    def add_message_handler(self, callback):
        """
        Add a message handler for all of the rdf requests.
        :param callback:
        :return:
        """

    def _receive_request_message(self, message):
        """
        Receive a message from the channel.  This should see if there is a new request that is pending and will execute
        all of the message handlers that have been assigned to this handler.
        :param message: incoming message from the channel.
        :return:
        """
        logger.info('Received a request message: %s' % message)

        # TODO: Check to see if there is an rdf request message in the payload.  This method will also be responsible
        # for handling all of the incoming respones and giving them to the appropriate callbacks.
        rdf_payload = message.get('rdf', None)
        if rdf_payload:
            command_type = rdf_payload.get('command', 'ignore')
            if command_type == 'request':
                for handler in self._handlers:
                    response = handler(rdf_payload)
                    if response:
                        self.xmpp['rho_bot_roster'].send_message(payload=response,
                                                                 thread_id=message.get('thread', None))
                    # TODO: generate a method that will respond to the message if a payload is returned by the handler
                    # and execute it in the scheduler.
                    pass
            elif command_type == 'response':
                thread_identifier = message.get('thread', None)
                if thread_identifier:
                    handler = self._pending_requests.get(thread_identifier, None)
                    if handler:
                        handler(rdf_payload)
        else:
            logger.debug('Skipping message handling')

    def _generate_cancel_event(self, callback, request_identifier):
        """
        Generate a callback that will cancel the handler and notify the callback that the handler has timed out.
        :param callback:
        :return:
        """
        def call_back_method():
            if request_identifier in self._pending_requests:
                del self._pending_requests[request_identifier]

            callback(payload=None, timeout=True)

        return call_back_method

rho_bot_rdf_publish = RDFPublish
