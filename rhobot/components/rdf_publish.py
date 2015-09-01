"""
Plugin that is responsible for publishing requests or responses to rdf messages in the channel.  Since IQ messages
cannot be broadcast to all of the members of a channel, this functionality will piggy back on messages instead.

Need to figure out how to handle all of the methods associated with the functionality.

For the response to a message it can be easily done by executing the command in a blocking thread and then respond to
it.

Promises provide the functionality for making requests and gathering results.  When selecting a single response, the
promise will be resolved immediately after the first response is received.

Promises selecting all responses will have to wait for the timeout to occur before resolving the promise.
"""

from sleekxmpp.plugins.base import base_plugin
from sleekxmpp.xmlstream import ElementBase, register_stanza_plugin
from sleekxmpp.plugins.xep_0004.stanza.form import Form
from sleekxmpp import Message
from rhobot.components.roster import RosterComponent
from rhobot.components.scheduler import Promise
from rhobot.components.storage import ResultCollectionPayload
import logging
import uuid
from enum import Enum
from rhobot.stanza_modification import patch_form_fields; patch_form_fields()

logger = logging.getLogger(__name__)


class RDFStanzaType(Enum):
    REQUEST = 'request'
    RESPONSE = 'response'
    CREATE = 'create'
    UPDATE = 'update'
    SEARCH_REQUEST = 'search'
    SEARCH_RESPONSE = 'search_response'


class RDFStanza(ElementBase):
    """
    Stanza responsible for requesting and responding to rdf requests.
    <rdf xmlns='rho:rdf' type='request|response'>
        <x xmlns='data'... />
        <source>
            <name>Some Name</name>
            <command>xmpp:jid@jiddomain.com?command;node=some_node;action=execute</command>
        </source>
    </rdf>

    source provides a command that can be used to search for other valid details.
    """
    name = 'rdf'
    namespace = 'rho:rdf'
    plugin_attrib = 'rdf'
    interfaces = {'type', }


class RDFSourceStanza(ElementBase):
    """
    Stanza responsible for providing details about the source of the data that is coming in.
    """
    name = 'source'
    namespace = 'rdf:rho'
    plugin_attrib = 'source'
    interfaces = {'name', 'command', }
    sub_interfaces = interfaces


class RDFPublish(base_plugin):
    """
    Service that will send out requests and farm out the incoming messages to the appropriate handlers.
    """

    name = 'rho_bot_rdf_publish'
    dependencies = {'rho_bot_roster', 'rho_bot_scheduler', }
    description = 'Configuration Plugin'

    def plugin_init(self):
        """
        Initialize instance variables for the service.
        :return:
        """
        register_stanza_plugin(Message, RDFStanza)
        register_stanza_plugin(RDFStanza, Form)
        register_stanza_plugin(RDFStanza, RDFSourceStanza)

        self.xmpp.add_event_handler(RosterComponent.CHANNEL_JOINED, self._channel_joined)

        self._pending_requests = dict()
        self._request_handlers = []
        self._create_handlers = []
        self._update_handlers = []
        self._search_handlers = []

    def _channel_joined(self, event):
        """
        When the channel is joined, add a message listener for all of the incoming requests and the responses that are
        made to requests made by this bot.
        :param event: ignored.
        :return: None
        """
        logger.info('Joined the registration channel')
        self.xmpp['rho_bot_roster'].add_message_received_listener(self._receive_message)

    def send_out_request(self, payload, timeout=10.0, allow_multiple=False):
        """
        Send out an rdf request for the provided payload.
        :param payload: the payload to serialize and then
        :param timeout: the timeout that will be used to cancel the request.
        :return: a promise
        """
        thread_identifier = str(uuid.uuid4())

        promise = Promise(self.xmpp['rho_bot_scheduler'])

        if allow_multiple:
            callback = self._generate_gather_all_data(promise, thread_identifier)
        else:
            callback = self._generate_single_fetch(promise, thread_identifier)

        self._pending_requests[thread_identifier] = dict(callback=callback,
                                                         results=ResultCollectionPayload())

        self._send_message(mtype=RDFStanzaType.REQUEST, payload=payload, thread_id=thread_identifier)

        self.xmpp['rho_bot_scheduler'].schedule_task(callback=self._generate_cancel_event(promise, thread_identifier),
                                                     delay=timeout)

        return promise

    def send_out_search(self, payload, timeout=10.0):
        """
        Send out a search request to all of the users that are currently in the channel.
        :param payload: payload to serialize and then send out.
        :param timeout: length of time in seconds before canceling the request.
        :return: promise containing all of the results.
        """
        thread_identifier = str(uuid.uuid4())

        promise = Promise(self.xmpp['rho_bot_scheduler'])

        self._pending_requests[thread_identifier] = dict(callback=self._generate_gather_all_data(promise,
                                                                                                 thread_identifier),
                                                         results=ResultCollectionPayload())

        self._send_message(mtype=RDFStanzaType.SEARCH_REQUEST, payload=payload, thread_id=thread_identifier)

        self.xmpp['rho_bot_scheduler'].schedule_task(callback=self._generate_cancel_event(promise, thread_identifier),
                                                     delay=timeout)

        return promise

    def publish_create(self, payload):
        """
        Publish a create message.
        :param payload:
        :return:
        """
        self._send_message(mtype=RDFStanzaType.CREATE, payload=payload)

    def publish_update(self, payload):
        """
        Publish an update message.
        :param payload:
        :return:
        """
        self._send_message(mtype=RDFStanzaType.UPDATE, payload=payload)

    def add_request_handler(self, callback):
        """
        Add a message handler for all of the rdf requests.
        :param callback:
        :return:
        """
        self._request_handlers.append(callback)

    def add_create_handler(self, callback):
        """
        Add a message handler for all of the create notifications.
        :param callback:
        :return:
        """
        self._create_handlers.append(callback)

    def add_update_handler(self, callback):
        """
        Add a message handler for all of the delete notifications.
        :param callback:
        :return:
        """
        self._update_handlers.append(callback)

    def add_search_handler(self, callback):
        """
        Add a message handler for all of the search notifications.
        :param callback:
        :return:
        """
        self._search_handlers.append(callback)

    def _populate_rdf(self, mtype='ignore', payload=None, source_command_node=None):

        result = RDFStanza()

        if isinstance(mtype, RDFStanzaType):
            result['type'] = mtype.value
        else:
            result['type'] = mtype

        if payload:
            result.append(payload.populate_payload())

        if source_command_node:
            source_stanza = RDFSourceStanza()
            source_stanza['name'] = self.xmpp.name
            source_stanza['command'] = 'xmpp:%s?command;node=%s' % (self.xmpp['rho_bot_roster'].get_jid(),
                                                                    source_command_node)
            result.append(source_stanza)

        return result

    def _send_message(self, mtype='ignore', payload=None, thread_id=None, source_command_node=None):
        """
        Create and RDF message and populate it with the payload for transmission.
        :param mtype:
        :param payload:
        :param thread_id:
        :return:
        """
        rdf_stanza = self._populate_rdf(mtype=mtype, payload=payload, source_command_node=source_command_node)

        self.xmpp['rho_bot_roster'].send_message(payload=rdf_stanza, thread_id=thread_id)

    def _receive_message(self, message):
        """
        Receive a message from the channel.  This should see if there is a new request that is pending and will execute
        all of the message handlers that have been assigned to this handler.
        :param message: incoming message from the channel.
        :return:
        """
        logger.debug('Received a request message: %s' % message)

        rdf_payload = message.get('rdf')
        message_type = rdf_payload.get('type', 'ignore')

        try:
            message_type = RDFStanzaType(message_type)

            if message_type == RDFStanzaType.REQUEST:
                self._request(message, rdf_payload)
            elif message_type == RDFStanzaType.RESPONSE:
                self._response(message, rdf_payload)
            elif message_type == RDFStanzaType.CREATE:
                self._create(message, rdf_payload)
            elif message_type == RDFStanzaType.UPDATE:
                self._update(message, rdf_payload)
            elif message_type == RDFStanzaType.SEARCH_REQUEST:
                self._search_request(message, rdf_payload)
            elif message_type == RDFStanzaType.SEARCH_RESPONSE:
                self._search_response(message, rdf_payload)
        except ValueError:
            logger.error('Unknown message type: %s' % message_type)

    def _request(self, message, rdf_payload):
        """
        Handle request messages.
        :param message:
        :param rdf_payload:
        :return:
        """
        for handler in self._request_handlers:
            response = handler(rdf_payload)
            if response:
                self._send_message(mtype=RDFStanzaType.RESPONSE, payload=response,
                                   thread_id=message.get('thread', None))

    def _response(self, message, rdf_payload):
        """
        Handle the response messages.
        :param message:
        :param rdf_payload:
        :return:
        """
        thread_identifier = message.get('thread', None)
        if thread_identifier:
            result = self._pending_requests.get(thread_identifier, None)

            if result:
                callback = self._pending_requests.get(thread_identifier, None)['callback']
                callback(rdf_payload)

    def _create(self, message, rdf_payload):
        """
        Handle create messages.
        :param message:
        :param rdf_payload:
        :return:
        """
        for handler in self._create_handlers:
            handler(rdf_payload)

    def _update(self, message, rdf_payload):
        """
        Handle update messages.
        :param message:
        :param rdf_payload:
        :return:
        """
        for handler in self._update_handlers:
            handler(rdf_payload)

    def _search_request(self, message, rdf_payload):
        """
        Handle search request message.
        :param message:
        :param rdf_payload:
        :return:
        """
        for handler in self._search_handlers:
            response = handler(rdf_payload)
            if response:
                self._send_message(mtype=RDFStanzaType.RESPONSE, payload=response,
                                   thread_id=message.get('thread', None))

    def _search_response(self, message, rdf_payload):
        """
        Handle the response messages.
        :param message:
        :param rdf_payload:
        :return:
        """
        thread_identifier = message.get('thread', None)
        if thread_identifier:
            result = self._pending_requests.get(thread_identifier, None)

            if result:
                callback = self._pending_requests.get(thread_identifier, None)['callback']
                callback(rdf_payload)

    def _generate_cancel_event(self, promise, request_identifier):
        """
        Generate a callback that will cancel the handler and notify the callback that the handler has timed out.
        :param promise:
        :return:
        """
        def call_back_method():
            result_container = self._pending_requests.get(request_identifier, None)

            if result_container:
                del self._pending_requests[request_identifier]
                promise.resolved(result_container['results'])

        return call_back_method

    def _generate_single_fetch(self, promise, thread_identifier):
        """
        Generates a single fetch handler.  This will take the first responder and use it to provide content back to the
        promise.
        :param promise:
        :param thread_identifier:
        :return:
        """
        def single_fetch(rdf):
            form = rdf['form']
            results_collection = ResultCollectionPayload(form)

            promise.resolved(results_collection)
            del self._pending_requests[thread_identifier]

        return single_fetch

    def _generate_gather_all_data(self, promise, thread_identifier):
        """
        Generates a handler that will gather all of the data that has been requested by the components in the channel.
        :param promise: promise that will be eventually resolved with data.
        :param thread_identifier: thread_identifier that will be used to store the contents.
        :return: generated method that can be called when data is received.
        """
        def multiple_fetch(rdf):

            result_container = self._pending_requests.get(thread_identifier, None)
            if result_container:
                form = rdf['form']
                results_collection = ResultCollectionPayload(form)
                results = result_container['results']
                results.append(*results_collection.results)

                # Store off the sources if necessary
                if rdf['source']:
                    if hasattr(results, 'sources'):
                        sources = results.sources
                    else:
                        sources = set()

                    if rdf['source']['command']:
                        sources.add((rdf['source']['name'], rdf['source']['command']))
                        results.sources = sources

        return multiple_fetch


rho_bot_rdf_publish = RDFPublish
