"""
Send out a single request and handle it correctly.
"""
import unittest
import mock
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.plugins.xep_0004 import Form, FormField, FieldOption
from sleekxmpp import Message
from rhobot.components.rdf_publish import rho_bot_rdf_publish, RDFStanzaType
from rhobot.components.storage import StoragePayload, ResultCollectionPayload, ResultPayload
from rdflib.namespace import FOAF, RDF, RDFS
from rhobot.namespace import RHO


class PublishCreateTestCase(unittest.TestCase):

    def setUp(self):
        self.scheduler_plugin = mock.MagicMock()
        self.roster_plugin = mock.MagicMock()

        plugins = {'rho_bot_scheduler': self.scheduler_plugin,
                   'rho_bot_roster': self.roster_plugin}

        def getitem(name):
            return plugins.get(name, False)

        self.xmpp = mock.MagicMock()
        self.xmpp.__getitem__.side_effect = getitem

        self.rdf_publisher = rho_bot_rdf_publish(self.xmpp, None)
        self.rdf_publisher.plugin_init()
        self.xmpp = mock.MagicMock

        register_stanza_plugin(FormField, FieldOption, iterable=True)
        register_stanza_plugin(Form, FormField, iterable=True)

    def test_send_request(self):

        payload = StoragePayload()
        payload.add_type(FOAF.Person, RHO.Owner)

        request_promise = self.rdf_publisher.send_out_request(payload)
        self.assertIsNotNone(request_promise)
        self.assertTrue(hasattr(request_promise, 'then'))

        # Verify the payload request.
        self.assertEqual(1, self.roster_plugin.send_message.call_count)

        args, kwargs = self.roster_plugin.send_message.call_args

        self.assertIn('thread_id', kwargs)
        self.assertIn('payload', kwargs)

        # Must have a payload, and a thread_id
        self.assertIsNotNone(kwargs['thread_id'])
        self.assertIsNotNone(kwargs['payload'])

        payload = kwargs['payload']
        self.assertEqual(payload['type'], RDFStanzaType.REQUEST.value)
        self.assertIn(str(FOAF.Person), payload['form'].get_fields()[str(RDF.type)].get_value())
        self.assertIn(str(RHO.Owner), payload['form'].get_fields()[str(RDF.type)].get_value())

    def test_timeout_request(self):
        payload = StoragePayload()
        payload.add_type(FOAF.Person, RHO.Owner)

        promise = self.rdf_publisher.send_out_request(payload)

        args, kwargs = self.scheduler_plugin.schedule_task.call_args
        callback = kwargs['callback']

        with mock.patch.object(target=promise, attribute='resolved') as mocked_method:
            callback()
            mocked_method.assert_called_with([])

    def test_empty_handle_request(self):

        payload = StoragePayload()
        payload.add_type(FOAF.Person, RHO.Owner)

        self.rdf_publisher.send_out_request(payload)

        # Verify the payload request.
        self.assertEqual(1, self.roster_plugin.send_message.call_count)

        args, kwargs = self.roster_plugin.send_message.call_args
        payload = kwargs['payload']

        message = Message()
        message.append(payload)
        message['thread'] = kwargs['thread_id']

        # Test empty request.
        self.rdf_publisher._receive_message(message)

    # I think this needs to go in the response handler unit tests.
    # def test_no_result(self):
    #     payload = StoragePayload()
    #     payload.add_type(FOAF.Person, RHO.Owner)
    #
    #     self.rdf_publisher.send_out_request(payload)
    #
    #     # Verify the payload request.
    #     self.assertEqual(1, self.roster_plugin.send_message.call_count)
    #
    #     args, kwargs = self.roster_plugin.send_message.call_args
    #     payload = kwargs['payload']
    #
    #     message = Message()
    #     message.append(payload)
    #     message['thread'] = kwargs['thread_id']
    #
    #     handler_mock = mock.Mock(return_value=None)
    #     self.rdf_publisher.add_request_handler(handler_mock)
    #
    #     self.rdf_publisher._receive_message(message)

    def test_response_received(self):

        publish_urn = 'rho:instances.owner'

        payload = StoragePayload()
        payload.add_type(FOAF.Person, RHO.Owner)

        promise = self.rdf_publisher.send_out_request(payload)

        args, kwargs = self.roster_plugin.send_message.call_args
        payload = kwargs['payload']
        thread_id = kwargs['thread_id']

        response_payload = ResultCollectionPayload()
        response_payload.append(ResultPayload(about=publish_urn, types=[FOAF.Person, RHO.Owner]))

        self.rdf_publisher._send_message(RDFStanzaType.RESPONSE, response_payload, thread_id)
        response_args, response_kwargs = self.roster_plugin.send_message.call_args

        payload = response_kwargs['payload']
        response_message = Message()
        response_message.append(payload)
        response_message['thread'] = response_kwargs['thread_id']

        with mock.patch.object(promise, attribute='resolved') as mock_promise_resolve:
            self.rdf_publisher._receive_message(response_message)

            mock_promise_resolve.assert_called_with([publish_urn])

    def test_responed_only_once(self):

        publish_urn = 'rho:instances.owner'

        payload = StoragePayload()
        payload.add_type(FOAF.Person, RHO.Owner)

        promise = self.rdf_publisher.send_out_request(payload)

        args, kwargs = self.roster_plugin.send_message.call_args
        payload = kwargs['payload']
        thread_id = kwargs['thread_id']

        response_payload = ResultCollectionPayload()
        response_payload.append(ResultPayload(about=publish_urn, types=[FOAF.Person, RHO.Owner]))

        self.rdf_publisher._send_message(RDFStanzaType.RESPONSE, response_payload, thread_id)
        response_args, response_kwargs = self.roster_plugin.send_message.call_args

        payload = response_kwargs['payload']
        response_message = Message()
        response_message.append(payload)
        response_message['thread'] = response_kwargs['thread_id']

        with mock.patch.object(promise, attribute='resolved') as mock_promise_resolve:
            self.rdf_publisher._receive_message(response_message)

            mock_promise_resolve.assert_called_with([publish_urn])

        with mock.patch.object(promise, attribute='resolved') as mock_promise_resolve:
            self.rdf_publisher._receive_message(response_message)

            mock_promise_resolve.assert_not_called()
