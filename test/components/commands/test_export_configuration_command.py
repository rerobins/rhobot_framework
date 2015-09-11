import logging; logging.basicConfig(level=logging.DEBUG)
from sleekxmpp.test import SleekTest
import unittest
import time


class ExportConfigurationTestCase(SleekTest):

    def setUp(self):
        self.session = {}
        self.stream_start(plugins=['xep_0050'])
        self.xmpp.register_plugin('rho_bot_scheduler', module='rhobot.components')
        self.xmpp.register_plugin('rho_bot_configuration', module='rhobot.components')
        self.xmpp.register_plugin('rho_bot_roster', module='rhobot.components')
        self.xmpp.register_plugin('export_configuration', module='rhobot.components.commands')

        self.scheduler = self.xmpp['rho_bot_scheduler']
        self.configuration = self.xmpp['rho_bot_configuration']
        self.roster = self.xmpp['rho_bot_roster']
        self.export_configuration = self.xmpp['export_configuration']

        self.scheduler.plugin_init()
        self.configuration.plugin_init()
        self.roster.plugin_init()
        self.export_configuration.plugin_init()

        self.scheduler.post_init()
        self.configuration.post_init()
        self.roster.post_init()
        self.export_configuration.post_init()

        # Set the room details in the muc plugin.
        self.xmpp['xep_0045'].ourNicks['room@host'] = 'room_nick'

    def tearDown(self):
        self.stream_close()

    def test_get_uri(self):
        self.assertEqual(self.export_configuration.get_command_uri(),
                         'xmpp:room@host/room_nick?command;node=export_configuration')
