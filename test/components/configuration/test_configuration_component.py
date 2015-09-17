"""
Unit tests for the configuration component.
"""
from sleekxmpp.test import SleekTest
import unittest
import time


class ConfigurationComponentTestCase(SleekTest):

    def setUp(self):
        from rhobot.components import register_core_plugins
        register_core_plugins()

        self.session = {}
        self.stream_start(plugins=['xep_0060', 'rho_bot_scheduler', 'rho_bot_configuration', ])
        self.scheduler = self.xmpp['rho_bot_scheduler']

        self.xmpp['rho_bot_configuration'].plugin_init()

    def tearDown(self):
        self.stream_close()

    def test_find_nodes_does_not_exist(self):

        self.xmpp['rho_bot_configuration']._start('session_start')

        # Make sure that the node has sent out it's initial request.
        self.send("""
            <iq to="tester@localhost" type="get" id="1">
                <query xmlns="http://jabber.org/protocol/disco#items" />
            </iq>
        """)

        # Fake receiving a message that doesn't contain the items.
        self.recv("""
            <iq from="tester@localhost" type="result" id="1" to="tester@localhost/full">
                <query xmlns="http://jabber.org/protocol/disco#items" />
            </iq>
        """)

        time.sleep(0.2)

        # Check to make sure that a new node has been created.
        self.send("""
            <iq to="tester@localhost" type="set" id="2">
                <pubsub xmlns="http://jabber.org/protocol/pubsub">
                    <create node="rho:configuration" />
                    <configure>
                        <x xmlns="jabber:x:data" type="submit">
                            <title>Node Configuration</title>
                            <field var="pubsub#access_model"><value>whitelist</value></field>
                            <field var="pubsub#persist_items"><value>1</value></field>
                            <field var="pubsub#max_items"><value>1</value></field>
                            <field var="FORM_TYPE"><value>http://jabber.org/protocol/pubsub#node_config</value></field>
                        </x>
                    </configure>
                </pubsub>
            </iq>
        """)

        # Send back the response when the node is created.
        self.recv("""
            <iq type="result"
                from="tester@localhost"
                to="tester@localhost/full"
                id="2"/>
        """)

        time.sleep(0.2)

        # Check to see if it requests the node now.
        self.send("""
            <iq to="tester@localhost" type="get" id="3">
                <pubsub xmlns="http://jabber.org/protocol/pubsub">
                    <items node="rho:configuration" />
                </pubsub>
            </iq>
        """)

        # Send back absolutely no configuration.
        self.recv("""
            <iq from="tester@localhost" type="result" id="3" to="tester@localhost/full">
                <pubsub xmlns="http://jabber.org/protocol/pubsub">
                    <items node="rho:configuration">
                        <item id="81725617-699c-4909-be22-8ae3721068b14">
                        </item>
                    </items>
                </pubsub>
            </iq>
        """)

        time.sleep(0.2)

        configuration = self.xmpp['rho_bot_configuration'].get_configuration()

        self.assertDictEqual(dict(), configuration)

    def test_configuratoin_defined(self):

        self.xmpp['rho_bot_configuration']._start('session_start')

        # Make sure that the node has sent out it's initial request.
        self.send("""
            <iq to="tester@localhost" type="get" id="1">
                <query xmlns="http://jabber.org/protocol/disco#items" />
            </iq>
        """)

        # Fake receiving a message that doesn't contain the items.
        self.recv("""
            <iq from="tester@localhost" type="result" id="1" to="tester@localhost/full">
                <query xmlns="http://jabber.org/protocol/disco#items">
                    <item node="rho:configuration" jid="tester@localhost" />
                </query>
            </iq>
        """)

        time.sleep(0.2)

        # Check to see if it requests the node now.
        self.send("""
            <iq to="tester@localhost" type="get" id="2">
                <pubsub xmlns="http://jabber.org/protocol/pubsub">
                    <items node="rho:configuration" />
                </pubsub>
            </iq>
        """)

        # Send back a configuration.
        self.recv("""
            <iq from="tester@localhost" type="result" id="2" to="tester@localhost/full">
                <pubsub xmlns="http://jabber.org/protocol/pubsub">
                    <items node="rho:configuration">
                        <item id="81725617-699c-4909-be22-8ae3721068b14">
                            <configuration xmlns="rho:configuration">
                                <entry>
                                    <key>access_token</key>
                                    <value>this_is_my_access_token</value>
                                </entry>
                                <entry>
                                    <key>secret</key>
                                    <value>this_is_my_secret</value>
                                </entry>
                            </configuration>
                        </item>
                    </items>
                </pubsub>
            </iq>
        """)

        time.sleep(0.2)

        configuration = self.xmpp['rho_bot_configuration'].get_configuration()

        self.assertDictEqual(dict(access_token='this_is_my_access_token',
                                  secret='this_is_my_secret'),
                             configuration)

    def test_get_values(self):

        self.xmpp['rho_bot_configuration'].get_configuration()['key'] = 'value'

        result = self.xmpp['rho_bot_configuration'].get_value('key', 'default')

        self.assertEquals(result, 'value')

        result = self.xmpp['rho_bot_configuration'].get_value('other_key', None)

        self.assertEquals(result, None)

        # Test an actual value to not be saved
        result = self.xmpp['rho_bot_configuration'].get_value('other_key', False, persist_if_missing=False)

        self.assertEquals(result, False)

        # Test an actual value to be saved
        result = self.xmpp['rho_bot_configuration'].get_value('other_key', False, persist_if_missing=True)

        self.assertEquals(result, False)

        self.send("""
            <iq to="tester@localhost" type="set" id="1">
                <pubsub xmlns="http://jabber.org/protocol/pubsub">
                    <publish node="rho:configuration">
                        <item>
                            <configuration xmlns="rho:configuration">
                                <entry>
                                    <key>key</key>
                                    <value>value</value>
                                </entry>
                                <entry>
                                    <key>other_key</key>
                                    <value>False</value>
                                </entry>
                            </configuration>
                        </item>
                    </publish>
                </pubsub>
            </iq>
        """)

    def test_merge_updates(self):

        self.xmpp['rho_bot_configuration'].merge_configuration(dict(key='value'), persist=False)

        result = self.xmpp['rho_bot_configuration'].get_value('key', 'default')

        self.assertEquals(result, 'value')

        # Test an actual value to be saved
        self.xmpp['rho_bot_configuration'].merge_configuration(dict(other_key=False), persist=True)

        self.send("""
            <iq to="tester@localhost" type="set" id="1">
                <pubsub xmlns="http://jabber.org/protocol/pubsub">
                    <publish node="rho:configuration">
                        <item>
                            <configuration xmlns="rho:configuration">
                                <entry>
                                    <key>key</key>
                                    <value>value</value>
                                </entry>
                                <entry>
                                    <key>other_key</key>
                                    <value>False</value>
                                </entry>
                            </configuration>
                        </item>
                    </publish>
                </pubsub>
            </iq>
        """)


suite = unittest.TestLoader().loadTestsFromTestCase(ConfigurationComponentTestCase)
