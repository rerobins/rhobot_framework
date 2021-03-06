"""
Unit tests for the configuration component.
"""
import time

from sleekxmpp.test import SleekTest


class TestRepresentationManager(SleekTest):

    def setUp(self):
        from rhobot.components import register_core_plugins
        register_core_plugins()

        self.session = {}
        self.stream_start(plugins=['xep_0050', 'rho_bot_scheduler', 'rho_bot_configuration', 'rho_bot_roster',
                                   'rho_bot_rdf_publish', 'rho_bot_storage_client', 'rho_bot_representation_manager',])

        self.scheduler = self.xmpp['rho_bot_scheduler']
        self.rdf_publish = self.xmpp['rho_bot_rdf_publish']
        self.storage_client = self.xmpp['rho_bot_storage_client']
        self.rho_bot_representation_manager = self.xmpp['rho_bot_representation_manager']
        self.roster = self.xmpp['rho_bot_roster']

        self.scheduler.plugin_init()
        self.storage_client.plugin_init()
        self.rdf_publish.plugin_init()
        # self.rho_bot_representation_manager.plugin_init()

        self.scheduler.post_init()
        self.storage_client.post_init()
        self.rdf_publish.post_init()
        self.rho_bot_representation_manager.post_init()

        def get_uri(self):
            """
            Return the URI for this bot.
            :return:
            """
            return 'xmpp:%s' % self.boundjid.bare

        self.xmpp.__class__.get_uri = get_uri
        self.xmpp.name = 'Bot Name'

        # Configure all of the plugins as necessary.
        self.roster._channel_name = 'conference@conference.example.org'

    def tearDown(self):
        self.stream_close()

    def test_representation_create(self):

        self.storage_client._storage_jid = 'storage@example.org/storage'
        self.rho_bot_representation_manager._start('asdf')

        time.sleep(0.2)

        self.send("""
            <iq type="set" to="storage@example.org/storage" id="1">
                <command xmlns="http://jabber.org/protocol/commands"
                    node="find_node"
                    action="execute">
                    <x xmlns="jabber:x:data" type="form">
                        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" type="list-multi">
                            <value>http://xmlns.com/foaf/0.1/Agent</value>
                            <value>http://www.w3.org/2000/01/rdf-schema#Resource</value>
                        </field>
                        <field var="http://www.w3.org/2000/01/rdf-schema#seeAlso" type="list-multi">
                            <value>xmpp:tester@localhost</value>
                            <validate xmlns="http://jabber.org/protocol/xdata-validate" datatype="xs:string" />
                        </field>
                    </x>
                </command>
            </iq>
        """)

        self.recv("""
            <iq type="set" to="storage@example.org/storage" id="1">
                <command xmlns="http://jabber.org/protocol/commands"
                    node="find_node"
                    action="completed">
                    <x xmlns="jabber:x:data" type="form">
                        <reported>
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#about" type="text-single" />
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" type="list-multi" />
                        </reported>
                    </x>
                </command>
            </iq>
        """)

        time.sleep(0.2)

        self.send("""
            <iq type="set" to="storage@example.org/storage" id="2">
                <command xmlns="http://jabber.org/protocol/commands"
                    node="create_node"
                    action="execute">
                    <x xmlns="jabber:x:data" type="form">
                        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" type="list-multi">
                            <value>http://xmlns.com/foaf/0.1/Agent</value>
                            <value>http://www.w3.org/2000/01/rdf-schema#Resource</value>
                        </field>
                        <field var="http://www.w3.org/2000/01/rdf-schema#seeAlso" type="list-multi">
                            <value>xmpp:tester@localhost</value>
                            <validate xmlns="http://jabber.org/protocol/xdata-validate" datatype="xs:string" />
                        </field>
                        <field var="http://xmlns.com/foaf/0.1/name" type="list-multi">
                            <value>Bot Name</value>
                            <validate xmlns="http://jabber.org/protocol/xdata-validate" datatype="xs:string" />
                        </field>
                    </x>
                </command>
            </iq>
        """)

        self.recv("""
         <iq type='result' from='storage@example.org/storage' to='tester@localhost/full' id='2'>
                <command xmlns="http://jabber.org/protocol/commands"
                    node="create_node"
                    action="completed">
                    <x xmlns="jabber:x:data" type="form">
                        <reported>
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#about" type="text-single" />
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" type="list-multi" />
                        </reported>
                        <item>
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#about">
                                <value>http://www.example.org/instance/Bot01</value>
                            </field>
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type">
                                <value>http://xmlns.com/foaf/0.1/Agent</value>
                                <value>http://www.w3.org/2000/01/rdf-schema#Resource</value>
                            </field>
                        </item>
                    </x>
                </command>
            </iq>
        """)

        time.sleep(0.2)

        self.send("""
            <message type="groupchat" to="conference@conference.example.org">
                <body>Some Data</body>
                <rdf xmlns="urn:rho:rdf" type="create">
                    <x xmlns="jabber:x:data" type="form">
                        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#about" type="text-single">
                            <value>http://www.example.org/instance/Bot01</value>
                        </field>
                        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" type="list-multi">
                            <value>http://xmlns.com/foaf/0.1/Agent</value>
                            <value>http://www.w3.org/2000/01/rdf-schema#Resource</value>
                        </field>
                    </x>
                </rdf>
            </message>
        """)

    def test_representation_update(self):

        self.storage_client._storage_jid = 'storage@example.org/storage'
        self.rho_bot_representation_manager._start('asdf')

        time.sleep(0.2)

        self.send("""
            <iq type="set" to="storage@example.org/storage" id="1">
                <command xmlns="http://jabber.org/protocol/commands"
                    node="find_node"
                    action="execute">
                    <x xmlns="jabber:x:data" type="form">
                        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" type="list-multi">
                            <value>http://xmlns.com/foaf/0.1/Agent</value>
                            <value>http://www.w3.org/2000/01/rdf-schema#Resource</value>
                        </field>
                        <field var="http://www.w3.org/2000/01/rdf-schema#seeAlso" type="list-multi">
                            <value>xmpp:tester@localhost</value>
                            <validate xmlns="http://jabber.org/protocol/xdata-validate" datatype="xs:string" />
                        </field>
                    </x>
                </command>
            </iq>
        """)

        self.recv("""
            <iq type="set" to="storage@example.org/storage" id="1">
                <command xmlns="http://jabber.org/protocol/commands"
                    node="find_node"
                    action="completed">
                    <x xmlns="jabber:x:data" type="form">
                        <reported>
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#about" type="text-single" />
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" type="list-multi" />
                        </reported>
                        <item>
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#about">
                                <value>http://www.example.org/instance/Bot01</value>
                            </field>
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type">
                                <value>http://xmlns.com/foaf/0.1/Agent</value>
                                <value>http://www.w3.org/2000/01/rdf-schema#Resource</value>
                            </field>
                        </item>
                    </x>
                </command>
            </iq>
        """)

        time.sleep(0.2)

        self.send("""
            <iq type="set" to="storage@example.org/storage" id="2">
                <command xmlns="http://jabber.org/protocol/commands"
                    node="update_node"
                    action="execute">
                    <x xmlns="jabber:x:data" type="form">
                        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#about" type="text-single">
                            <value>http://www.example.org/instance/Bot01</value>
                        </field>
                        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" type="list-multi">
                            <value>http://xmlns.com/foaf/0.1/Agent</value>
                            <value>http://www.w3.org/2000/01/rdf-schema#Resource</value>
                        </field>
                        <field var="http://www.w3.org/2000/01/rdf-schema#seeAlso" type="list-multi">
                            <value>xmpp:tester@localhost</value>
                            <validate xmlns="http://jabber.org/protocol/xdata-validate" datatype="xs:string" />
                        </field>
                        <field var="http://xmlns.com/foaf/0.1/name" type="list-multi">
                            <value>Bot Name</value>
                            <validate xmlns="http://jabber.org/protocol/xdata-validate" datatype="xs:string" />
                        </field>
                    </x>
                </command>
            </iq>
        """)

        self.recv("""
         <iq type='result' from='storage@example.org/storage' to='tester@localhost/full' id='2'>
                <command xmlns="http://jabber.org/protocol/commands"
                    node="update_node"
                    action="completed">
                    <x xmlns="jabber:x:data" type="form">
                        <reported>
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#about" type="text-single" />
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" type="list-multi" />
                        </reported>
                        <item>
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#about">
                                <value>http://www.example.org/instance/Bot01</value>
                            </field>
                            <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type">
                                <value>http://xmlns.com/foaf/0.1/Agent</value>
                                <value>http://www.w3.org/2000/01/rdf-schema#Resource</value>
                            </field>
                        </item>
                    </x>
                </command>
            </iq>
        """)

        time.sleep(0.2)

        self.send("""
            <message type="groupchat" to="conference@conference.example.org">
                <body>Some Data</body>
                <rdf xmlns="urn:rho:rdf" type="update">
                    <x xmlns="jabber:x:data" type="form">
                        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#about" type="text-single">
                            <value>http://www.example.org/instance/Bot01</value>
                        </field>
                        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" type="list-multi">
                            <value>http://xmlns.com/foaf/0.1/Agent</value>
                            <value>http://www.w3.org/2000/01/rdf-schema#Resource</value>
                        </field>
                    </x>
                </rdf>
            </message>
        """)
