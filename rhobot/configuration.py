"""
Install the configuration details for the application.
"""
import ConfigParser
import logging

logger = logging.getLogger(__name__)

_configuration_parser = ConfigParser.ConfigParser()

BOT_SECTION_NAME = 'bot'
NAME_KEY = 'name'

CONNECTION_SECTION_NAME = 'connection'
JID_KEY = 'jid'
PASSWORD_KEY = 'password'

MUC_SECTION_NAME = 'muc'
ROOM_KEY = 'room'
ROOM_NICK_KEY = 'room_nick'


def get_configuration():
    global _configuration_parser
    return _configuration_parser


def load_file(filename):
    """
    Load the filename into the configuration parser.
    :param filename:
    :return:
    """
    global _configuration_parser
    logger.info('Loading configuration: %s' % filename)
    _configuration_parser.read(filename)

# Install the default parameters.
_configuration_parser.add_section(BOT_SECTION_NAME)
_configuration_parser.set(BOT_SECTION_NAME, NAME_KEY, 'bot_name')

_configuration_parser.add_section(CONNECTION_SECTION_NAME)
_configuration_parser.set(CONNECTION_SECTION_NAME, JID_KEY, 'user@host/resource')
_configuration_parser.set(CONNECTION_SECTION_NAME, PASSWORD_KEY, 'password')

_configuration_parser.add_section(MUC_SECTION_NAME)
_configuration_parser.set(MUC_SECTION_NAME, ROOM_KEY, 'room@host')
_configuration_parser.set(MUC_SECTION_NAME, ROOM_NICK_KEY, 'room_nick')
