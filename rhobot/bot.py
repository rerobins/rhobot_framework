import logging
import logging.config
import json

import sleekxmpp
import os
from rhobot import configuration
from rhobot.stanza_modification import patch_form_fields
patch_form_fields()

if os.path.exists('logging.json'):
    with open('logging.json', 'rt') as f:
        config = json.load(f)
        logging.config.dictConfig(config)
else:
    logging.basicConfig()

logger = logging.getLogger(__name__)


class RhoBot(sleekxmpp.ClientXMPP):

    def __init__(self):
        jid = configuration.get_configuration().get(configuration.CONNECTION_SECTION_NAME,
                                                    configuration.JID_KEY)
        password = configuration.get_configuration().get(configuration.CONNECTION_SECTION_NAME,
                                                         configuration.PASSWORD_KEY)
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.register_plugin('xep_0199')  # XMPP Ping
        self.register_plugin('rho_bot_scheduler', module='rhobot.components')
        self.register_plugin('rho_bot_configuration', module='rhobot.components')
        self.register_plugin('rho_bot_roster', module='rhobot.components')
        self.register_plugin('reset_configuration', module='rhobot.components.commands')
        self.register_plugin('export_configuration', module='rhobot.components.commands')
        self.register_plugin('import_configuration', module='rhobot.components.commands')

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
