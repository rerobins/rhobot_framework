"""
Unit tests for the configuration component.
"""
from sleekxmpp.test import SleekTest
from rhobot.components.storage import StoragePayload, ResultCollectionPayload, ResultPayload
from rhobot.components.storage.namespace import NEO4J
from rdflib.namespace import FOAF
import time


class ExecuteCypherTestCase(SleekTest):

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

    def test_execute_cypher(self):

        self.storage_client._store_found('storage@example.org/storage')

        payload = StoragePayload()
        payload.add_property(NEO4J.cypher, 'Match (n) RETURN n LIMIT 25')

        promise = self.storage_client.execute_cypher(payload)

        def handle_result(result):
            self.session['result'] = result

        promise.then(handle_result)

        self.assertTrue(hasattr(promise, 'then'))

        self.send("""
                <iq type="set" to="storage@example.org/storage" id="1">
                    <command xmlns="http://jabber.org/protocol/commands"
                        node="cypher"
                        action="execute">
                        <x xmlns="jabber:x:data" type="form">
                            <field var="http://www.neo4j.com/terms/#cypher" type="list-multi">
                                <value>Match (n) RETURN n LIMIT 25</value>
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
                           node='cypher'
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

    def test_no_cypher_defined(self):

        self.storage_client._store_found('storage@example.org/storage')

        payload = StoragePayload()

        promise = self.storage_client.execute_cypher(payload)

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
        payload.add_property(NEO4J.cypher, 'Match (n) RETURN n LIMIT 25')

        promise = self.storage_client.execute_cypher(payload)

        def handle_result(result):
            self.session['result'] = result

        def handle_error(result):
            self.session['error'] = result

        promise.then(handle_result, handle_error)

        self.assertTrue(hasattr(promise, 'then'))

        time.sleep(0.2)

        self.assertNotIn('result', self.session)
        self.assertIn('error', self.session)

