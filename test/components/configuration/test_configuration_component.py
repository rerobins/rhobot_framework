"""
Unit tests for the configuration component.
"""
from rhobot.components import rho_bot_configuration
from sleekxmpp.plugins.xep_0004 import Form
import unittest
import mock
import time


class ConfigurationComponentTestCase(unittest.TestCase):

    def setUp(self):
        self.pubsub_plugin = mock.MagicMock()
        self.form_plugin = mock.Mock()
        self.form_plugin.make_form = mock.Mock(return_value=Form())

        plugins = {'xep_0060': self.pubsub_plugin,
                   'xep_0004': self.form_plugin}

        def getitem(name):
            return plugins.get(name, False)

        self.xmpp = mock.MagicMock()
        self.xmpp.__getitem__.side_effect = getitem

        self.configuration_plugin = rho_bot_configuration(self.xmpp, None)

    def test_node_not_defined(self):

        self.configuration_plugin._start('event')

        self.assertEqual(self.pubsub_plugin.get_nodes.call_count, 1)
        args, kwargs = self.pubsub_plugin.get_nodes.call_args
        callback = kwargs['callback']

        stanza = dict(disco_items=dict(items=[]))
        callback(stanza)

        self.assertEqual(self.pubsub_plugin.create_node.call_count, 1)
        args, kwargs = self.pubsub_plugin.create_node.call_args

        self.assertEqual(self.configuration_plugin._configuration_data_node, kwargs['node'])

        self.assertIsNotNone(kwargs['config'])
        self.assertEqual(kwargs['config'].get_fields().get('pubsub#access_model').get_value(), 'whitelist')
        self.assertEqual(kwargs['config'].get_fields().get('pubsub#persist_items').get_value(), '1')
        self.assertEqual(kwargs['config'].get_fields().get('pubsub#max_items').get_value(), '1')




suite = unittest.TestLoader().loadTestsFromTestCase(ConfigurationComponentTestCase)
