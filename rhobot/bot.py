import logging
import sleekxmpp
from rhobot import configuration
from rhobot.components import register_core_plugins


# Register all of the core plugins.
register_core_plugins()

# Configure the logging for this file.
logger = logging.getLogger(__name__)


class RhoBot(sleekxmpp.ClientXMPP):

    required_plugins = ['rho_bot_roster', 'xep_0199', ]

    def __init__(self):
        # Set up the configuration details to call the super constructor.
        jid = configuration.get_configuration().get(configuration.CONNECTION_SECTION_NAME,
                                                    configuration.JID_KEY)
        password = configuration.get_configuration().get(configuration.CONNECTION_SECTION_NAME,
                                                         configuration.PASSWORD_KEY)

        logger.info('Attempting to configure with: %s %s' % (jid, password))

        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # Set up the configuration details for the name of the bot.
        self.name = configuration.get_configuration().get(configuration.BOT_SECTION_NAME,
                                                          configuration.NAME_KEY)

        # Register the plugins
        for plugin in self.required_plugins:
            self.register_plugin(plugin)

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler('session_start', self.start)

    def start(self, event):
        """
        Process the session_start event.
        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.
        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        self.get_roster()

    def get_uri(self):
        """
        Return the URI for this bot.
        :return:
        """
        return 'xmpp:%s' % self.boundjid.bare

    def add_required_plugin(self, *plugin_names):
        """
        Add a list of required plugins for the bot.
        :param plugin_names: plugin names.
        :return:
        """
        self.plugin_whitelist += plugin_names


if __name__ == '__main__':

    import optparse

    parser = optparse.OptionParser()
    parser.add_option('-c', dest='filename', help='Configuration file for the bot', default='rhobot.conf')
    (options, args) = parser.parse_args()

    configuration.load_file(options.filename)

    xmpp = RhoBot()
    # xmpp.register_plugin('rho_bot_storage_client', module='rhobot.components.storage_client')

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        xmpp.process(block=True)
    else:
        print('Unable to connect.')
