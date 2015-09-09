"""
Unit tests for the configuration component.
"""
from sleekxmpp.test import SleekTest
from rhobot.components.storage import StoragePayload, ResultCollectionPayload, ResultPayload
from rdflib.namespace import FOAF
import time


class GetNodeTestCase(SleekTest):

    def setUp(self):
        self.session = {}
        self.stream_start(plugins=['xep_0050'])
        self.xmpp.register_plugin('rho_bot_scheduler', module='rhobot.components')
        self.xmpp.register_plugin('rho_bot_storage_client', module='rhobot.components')
        self.scheduler = self.xmpp['rho_bot_scheduler']
        self.storage_client = self.xmpp['rho_bot_storage_client']

        self.scheduler.plugin_init()
        self.storage_client.plugin_init()
        self.storage_client.post_init()

    def tearDown(self):
        self.stream_close()

    def test_get_node(self):

        self.storage_client._store_found('storage@example.org/storage')

        payload = StoragePayload()
        payload.about = 'http://www.example.org/instance/01'
        payload.add_type(FOAF.Person)
        payload.add_property(FOAF.name, 'Robert')

        promise = self.storage_client.get_node(payload)

        def handle_result(result):
            self.session['result'] = result

        promise.then(handle_result)

        self.assertTrue(hasattr(promise, 'then'))

        self.send("""
                <iq type="set" to="storage@example.org/storage" id="1">
                    <command xmlns="http://jabber.org/protocol/commands"
                        node="get_node"
                        action="execute">
                        <x xmlns="jabber:x:data" type="form">
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#about" type="text-single">
                                <value>http://www.example.org/instance/01</value>
                            </field>
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" type="list-multi">
                                <value>http://xmlns.com/foaf/0.1/Person</value>
                            </field>
                            <field var="http://xmlns.com/foaf/0.1/name" type="list-multi">
                                <value>Robert</value>
                                <rdftype xmlns="urn:rho:rdf" type="http://www.w3.org/2000/01/rdf-schema#Literal" />
                            </field>
                        </x>
                    </command>
                </iq>
            """, use_values=False)

        self.assertNotIn('result', self.session)

        self.recv("""
                <iq type='result' from='storage@example.org/storage' to='tester@localhost/full' id='1'>
                    <command xmlns='http://jabber.org/protocol/commands'
                           sessionid='list:20020923T213616Z-700'
                           node='get_node'
                           status='completed'>
                            %s
                    </command>
                </iq>
            """ % payload.populate_payload())

        time.sleep(0.2)

        self.assertIn('result', self.session)

        result = self.session['result']

        self.assertEqual(result.about, 'http://www.example.org/instance/01')
        self.assertEquals(result.types[0], str(FOAF.Person))

    def test_no_about_defined(self):

        self.storage_client._store_found('storage@example.org/storage')

        payload = StoragePayload()
        payload.add_type(FOAF.Person)
        payload.add_property(FOAF.name, 'Robert')

        promise = self.storage_client.get_node(payload)

        def handle_result(result):
            self.session['result'] = result

        def handle_error(result):
            self.session['error'] = result

        promise.then(handle_result, handle_error)

        self.assertTrue(hasattr(promise, 'then'))

        time.sleep(0.2)

        self.assertNotIn('result', self.session)
        self.assertIn('error', self.session)

    def test_no_storage_defined(self):

        payload = StoragePayload()
        payload.about = 'some_urn'
        payload.add_type(FOAF.Person)
        payload.add_property(FOAF.name, 'Robert')

        promise = self.storage_client.get_node(payload)

        def handle_result(result):
            self.session['result'] = result

        def handle_error(result):
            self.session['error'] = result

        promise.then(handle_result, handle_error)

        self.assertTrue(hasattr(promise, 'then'))

        time.sleep(0.2)

        self.assertNotIn('result', self.session)
        self.assertIn('error', self.session)

