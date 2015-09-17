"""
Unit tests for the configuration component.
"""
from sleekxmpp.test import SleekTest
from rhobot.components.storage import StoragePayload, ResultCollectionPayload, ResultPayload
from rdflib.namespace import FOAF
import time


class CreateNodeTestCase(SleekTest):

    def setUp(self):
        from rhobot.components import register_core_plugins
        register_core_plugins()

        self.session = {}
        self.stream_start(plugins=['rho_bot_storage_client', ])
        self.scheduler = self.xmpp['rho_bot_scheduler']
        self.storage_client = self.xmpp['rho_bot_storage_client']

        self.scheduler.plugin_init()
        self.storage_client.plugin_init()
        self.storage_client.post_init()

    def tearDown(self):
        self.stream_close()

    def test_create_node(self):

        self.storage_client._store_found('storage@example.org/storage')

        payload = StoragePayload()
        payload.add_type(FOAF.Person)
        payload.add_property(FOAF.name, 'Robert')

        promise = self.storage_client.create_node(payload)

        def handle_result(result):
            self.session['result'] = result

        promise.then(handle_result)

        self.assertTrue(hasattr(promise, 'then'))

        self.send("""
            <iq type="set" to="storage@example.org/storage" id="1">
                <command xmlns="http://jabber.org/protocol/commands"
                    node="create_node"
                    action="execute">
                    <x xmlns="jabber:x:data" type="form">
                        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" type="list-multi">
                            <value>http://xmlns.com/foaf/0.1/Person</value>
                        </field>
                        <field var="http://xmlns.com/foaf/0.1/name" type="list-multi">
                            <value>Robert</value>
                            <validate xmlns="http://jabber.org/protocol/xdata-validate" datatype="xs:string" />
                        </field>
                    </x>
                </command>
            </iq>
        """)

        self.assertNotIn('result', self.session)

        result_payload = ResultCollectionPayload()
        result_payload.append(ResultPayload(about='http://www.example.org/instance/01',
                                            types=[FOAF.Person]))

        self.recv("""
            <iq type='result' from='storage@example.org/storage' to='tester@localhost/full' id='1'>
                <command xmlns='http://jabber.org/protocol/commands'
                       sessionid='list:20020923T213616Z-700'
                       node='create_node'
                       status='completed'>
                        %s
                </command>
            </iq>
        """ % result_payload.populate_payload())

        time.sleep(0.2)

        self.assertIn('result', self.session)

        result = self.session['result']

        self.assertEqual(1, len(result.results))

        self.assertEqual(result.results[0].about, 'http://www.example.org/instance/01')
        self.assertEquals(result.results[0].types[0], str(FOAF.Person))

    def test_no_storage_defined(self):

        payload = StoragePayload()
        payload.add_type(FOAF.Person)
        payload.add_property(FOAF.name, 'Robert')

        promise = self.storage_client.create_node(payload)

        def handle_result(result):
            self.session['result'] = result

        def handle_error(result):
            self.session['error'] = result

        promise.then(handle_result, handle_error)

        self.assertTrue(hasattr(promise, 'then'))

        time.sleep(0.2)

        self.assertNotIn('result', self.session)
        self.assertIn('error', self.session)

