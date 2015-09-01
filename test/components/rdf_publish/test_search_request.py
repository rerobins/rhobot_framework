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


class SearchRequestTestCase(unittest.TestCase):

    def setUp(self):
        self.scheduler_plugin = mock.MagicMock()
        self.roster_plugin = mock.MagicMock(**{'get_jid.return_value': 'rhobot@conference.local/bot'})

        plugins = {'rho_bot_scheduler': self.scheduler_plugin,
                   'rho_bot_roster': self.roster_plugin}

        def getitem(name):
            return plugins.get(name, False)

        self.xmpp = mock.MagicMock()
        type(self.xmpp).name = mock.PropertyMock(return_value='RhoBot Name')
        self.xmpp.__getitem__.side_effect = getitem

        self.rdf_publisher = rho_bot_rdf_publish(self.xmpp, None)
        self.rdf_publisher.plugin_init()
        self.xmpp = mock.MagicMock

        register_stanza_plugin(FormField, FieldOption, iterable=True)
        register_stanza_plugin(Form, FormField, iterable=True)

    def test_send_request(self):

        payload = StoragePayload()
        payload.add_type(FOAF.Person, RHO.Owner)

        request_promise = self.rdf_publisher.send_out_search(payload)
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
        self.assertEqual(payload['type'], RDFStanzaType.SEARCH_REQUEST.value)
        self.assertIn(str(FOAF.Person), payload['form'].get_fields()[str(RDF.type)].get_value())
        self.assertIn(str(RHO.Owner), payload['form'].get_fields()[str(RDF.type)].get_value())

    def test_timeout_request(self):
        payload = StoragePayload()
        payload.add_type(FOAF.Person, RHO.Owner)

        promise = self.rdf_publisher.send_out_search(payload)

        args, kwargs = self.scheduler_plugin.schedule_task.call_args
        callback = kwargs['callback']

        with mock.patch.object(target=promise, attribute='resolved') as mocked_method:
            callback()
            self.assertEqual(1, mocked_method.call_count)
            self.assertEqual([], mocked_method.call_args[0][0].results)

    def test_response_received(self):

        publish_urn = 'rho:instances.owner'

        payload = StoragePayload()
        payload.add_type(FOAF.Person, RHO.Owner)

        promise = self.rdf_publisher.send_out_request(payload, allow_multiple=True)

        args, kwargs = self.roster_plugin.send_message.call_args
        payload = kwargs['payload']
        thread_id = kwargs['thread_id']

        args, kwargs = self.scheduler_plugin.schedule_task.call_args
        callback = kwargs['callback']

        response_payload = ResultCollectionPayload()
        response_payload.append(ResultPayload(about=publish_urn, types=[FOAF.Person, RHO.Owner]))

        self.rdf_publisher._send_message(RDFStanzaType.SEARCH_RESPONSE, response_payload, thread_id)
        response_args, response_kwargs = self.roster_plugin.send_message.call_args

        payload = response_kwargs['payload']
        response_message = Message()
        response_message.append(payload)
        response_message['thread'] = response_kwargs['thread_id']

        with mock.patch.object(promise, attribute='resolved') as mock_promise_resolve:
            self.rdf_publisher._receive_message(response_message)

            mock_promise_resolve.assert_not_called()

            callback()

            self.assertEqual(1, mock_promise_resolve.call_count)
            args, kwargs = mock_promise_resolve.call_args

            result = [rdf.about for rdf in args[0].results]

            self.assertEqual(result, [publish_urn])

            # Should not have any sources defined.
            callback_results = args[0]

            self.assertFalse(hasattr(callback_results, 'sources'))

    def test_retrieve_all(self):

        publish_urn = 'rho:instances.owner'

        payload = StoragePayload()
        payload.add_type(FOAF.Person, RHO.Owner)

        promise = self.rdf_publisher.send_out_request(payload, allow_multiple=True)

        args, kwargs = self.roster_plugin.send_message.call_args
        payload = kwargs['payload']
        thread_id = kwargs['thread_id']

        args, kwargs = self.scheduler_plugin.schedule_task.call_args
        callback = kwargs['callback']

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

            mock_promise_resolve.assert_not_called()

        with mock.patch.object(promise, attribute='resolved') as mock_promise_resolve:
            self.rdf_publisher._receive_message(response_message)

            mock_promise_resolve.assert_not_called()

        with mock.patch.object(promise, attribute='resolved') as mock_promise_resolve:

            callback()

            self.assertEqual(1, mock_promise_resolve.call_count)
            args, kwargs = mock_promise_resolve.call_args

            result = [rdf.about for rdf in args[0].results]

            self.assertEqual(result, [publish_urn, publish_urn])

            # Should not have any sources defined.
            callback_results = args[0]

            self.assertFalse(hasattr(callback_results, 'sources'))

    def test_sources_retrieved(self):

        publish_urn = 'rho:instances.owner'

        payload = StoragePayload()
        payload.add_type(FOAF.Person, RHO.Owner)

        promise = self.rdf_publisher.send_out_request(payload, allow_multiple=True)

        args, kwargs = self.roster_plugin.send_message.call_args
        payload = kwargs['payload']
        thread_id = kwargs['thread_id']

        args, kwargs = self.scheduler_plugin.schedule_task.call_args
        callback = kwargs['callback']

        response_payload = ResultCollectionPayload()
        response_payload.append(ResultPayload(about=publish_urn, types=[FOAF.Person, RHO.Owner]))

        search_command_node = 'search_command'

        self.rdf_publisher._send_message(RDFStanzaType.RESPONSE, response_payload, thread_id,
                                         source_command_node=search_command_node)
        response_args, response_kwargs = self.roster_plugin.send_message.call_args

        payload = response_kwargs['payload']
        response_message = Message()
        response_message.append(payload)
        response_message['thread'] = response_kwargs['thread_id']

        with mock.patch.object(promise, attribute='resolved') as mock_promise_resolve:
            self.rdf_publisher._receive_message(response_message)

            mock_promise_resolve.assert_not_called()

        with mock.patch.object(promise, attribute='resolved') as mock_promise_resolve:

            callback()

            self.assertEqual(1, mock_promise_resolve.call_count)
            args, kwargs = mock_promise_resolve.call_args

            result_payload = args[0]

            result = [rdf.about for rdf in result_payload.results]

            self.assertEqual(result, [publish_urn, ])

            self.assertTrue(hasattr(result_payload, 'sources'))

            sources = list(result_payload.sources)

            self.assertEqual(1, len(sources))

            self.assertEqual('RhoBot Name', sources[0][0])
            self.assertEqual('xmpp:rhobot@conference.local/bot?command;node=%s' % search_command_node,
                             sources[0][1])

