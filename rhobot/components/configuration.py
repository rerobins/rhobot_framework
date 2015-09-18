"""
Component that will handle the storing of details in xmpp for configuration.
"""
import logging

from sleekxmpp.plugins.base import base_plugin
from sleekxmpp.xmlstream import ElementBase, register_stanza_plugin

logger = logging.getLogger(__name__)


class ConfigurationStanza(ElementBase):
    """
    Stanza responsible for handling the configuration core.
    <configuration xmlns='rho:configuration'>
        <entry>
          <key>some_key</key>
          <value>some_value</value>
        </entry>
    </configuration>
    """
    name = 'configuration'
    namespace = 'rho:configuration'
    plugin_attrib = 'configuration'
    interfaces = {}
    sub_interfaces = {}

    def add_entry(self, key, value):
        entry_stanza = EntryStanza()
        entry_stanza['key'] = str(key)
        entry_stanza['value'] = str(value)
        self.append(entry_stanza)


class EntryStanza(ElementBase):
    """
    Entry Stanza.
    """
    name = 'entry'
    namespace = 'rho:configuration'
    plugin_attrib = 'entry'
    plugin_multi_attrib = 'entries'
    interfaces = {'key', 'value'}
    sub_interfaces = interfaces


class BotConfiguration(base_plugin):

    CONFIGURATION_RECEIVED_EVENT = 'rho::configuration_received'
    CONFIGURATION_UPDATED_EVENT = 'rho::configuration_updated'
    _configuration_data_node = 'rho:configuration'
    name = 'rho_bot_configuration'
    dependencies = {'xep_0060', 'rho_bot_scheduler', }
    description = 'RHO: Configuration Plugin'

    def plugin_init(self):
        """
        Configure the plugin to handle the private storage of data.
        :return:
        """
        self._configuration = dict()
        register_stanza_plugin(ConfigurationStanza, EntryStanza, iterable=True)
        self.xmpp.add_event_handler("session_start", self._start)

    def _start(self, event):
        """
        When connected to the service, request the configuration details for the object.  When finished, notify all
        listeners that configuration details have been fetched from the server.
        :return:
        """
        promise = self.xmpp['rho_bot_scheduler'].promise()
        self.xmpp['xep_0060'].get_nodes(jid=self.xmpp.boundjid.bare,
                                        callback=self.xmpp['rho_bot_scheduler'].generate_callback_promise(promise))
        promise = promise.then(self._found_nodes)
        promise = promise.then(None, self._create_node)
        promise = promise.then(self._fetch_configuration)
        promise.then(self._configuration_data_retrieved)

    def _found_nodes(self, stanza):
        """
        Check to see if the configuration node is defined or not.  If it's not defined, then create it.
        :param stanza:
        :return:
        """
        promise = self.xmpp['rho_bot_scheduler'].promise()

        logger.info('Found Nodes: %s' % stanza)

        found = False
        for item in stanza['disco_items']['items']:
            if item[1] == self._configuration_data_node:
                found = True
                break

        if found:
            promise.resolved(None)
        else:
            promise.rejected('Node not found')

        return promise

    def _fetch_configuration(self, ignored):
        """
        Request that the configuration be loaded.
        :return:
        """
        promise = self.xmpp['rho_bot_scheduler'].promise()
        logger.info('Fetching Configuration: %s' % self._configuration_data_node)
        self.xmpp['xep_0060'].get_items(jid=self.xmpp.boundjid.bare, node=self._configuration_data_node,
                                        callback=self.xmpp['rho_bot_scheduler'].generate_callback_promise(promise))

        return promise

    def _create_node(self, ignored):
        """
        Create the configuration storage node, and then store the data.
        :return:
        """
        promise = self.xmpp['rho_bot_scheduler'].promise()

        logger.info('Creating node: %s' % self._configuration_data_node)

        configuration_form = self.xmpp['xep_0004'].make_form(ftype='submit', title='Node Configuration')
        configuration_form.add_field(var='pubsub#access_model', value='whitelist')
        configuration_form.add_field(var='pubsub#persist_items', value='1')
        configuration_form.add_field(var='pubsub#max_items', value='1')

        self.xmpp['xep_0060'].create_node(jid=self.xmpp.boundjid.bare,
                                          node=self._configuration_data_node,
                                          callback=self.xmpp['rho_bot_scheduler'].generate_callback_promise(promise),
                                          config=configuration_form)

        return promise

    def _configuration_data_retrieved(self, stanza):
        """
        Call back that is called when the data is retrieved.

        Translates the stanza into configuration details and then notifies listeners that the configuration has been
        retrieved.
        :return:
        """
        logger.debug('Received configuration data: %s' % stanza)

        configuration_node = None
        for item in stanza['pubsub']['items']['substanzas']:
            configuration_node = item.get_payload()

        if configuration_node:
            configuration = ConfigurationStanza(xml=configuration_node)
            if 'entries' in configuration.keys():
                for entry in configuration['entries']:
                    self._configuration[entry['key']] = entry['value']

        self.xmpp.event(self.CONFIGURATION_RECEIVED_EVENT)

    def store_data(self):
        """
        Store data into the pub subscribe values.
        :return:
        """
        configuration_stanza = ConfigurationStanza()

        for key in sorted(self._configuration.keys()):
            configuration_stanza.add_entry(key, self._configuration[key])

        self.xmpp['xep_0060'].publish(jid=self.xmpp.boundjid.bare, payload=configuration_stanza,
                                      node=self._configuration_data_node,
                                      block=False)

        self.xmpp.event(self.CONFIGURATION_UPDATED_EVENT)

    def get_configuration(self):
        """
        Return a configuration dictionary for this bot.
        :return:
        """
        return self._configuration

    def get_value(self, key, default=None, persist_if_missing=True):
        """
        Returns the value of the key, or the default value.  If the default value is returned, then the default value
        is persisted.
        :param key:
        :param default:
        :param persist_if_missing: should the value be persisted if it's not in the configuration value.
        :return:
        """

        if key in self._configuration:
            return self._configuration[key]
        elif default is not None and persist_if_missing:
            self._configuration[key] = default
            self.store_data()

        return default

    def merge_configuration(self, configuration_dictionary, persist=True):
        """
        Merge the configuration dictionary into the current configuration.
        :param configuration_dictionary:
        :param persist: should the configuration be persisted if missing.
        :return:
        """
        self._configuration.update(configuration_dictionary)
        if persist:
            self.store_data()

rho_bot_configuration = BotConfiguration
