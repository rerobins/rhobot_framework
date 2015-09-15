import logging
from sleekxmpp.plugins.base import base_plugin

logger = logging.getLogger(__name__)


class BaseCommand(base_plugin):
    """
    Abstract implementation of a base command.
    """

    default_identifier = 'base_command_identifier'
    default_name = 'Base Command Name'
    default_dependencies = {'xep_0050', 'rho_bot_roster', }

    def __init__(self, *args, **kwargs):
        super(BaseCommand, self).__init__(*args, **kwargs)
        self.initialize_command()

    def initialize_command(self):
        """
        Initialize the command.
        :return:
        """
        logger.debug('Initialize Command')
        self._initialize_command(self.default_identifier, self.default_name, {})

    def _initialize_command(self, identifier, name, additional_dependencies=None):
        """
        Initialization of the command.
        :param identifier: identifier that will be used to determine how other bots reference this command.
        :param name: human readable name of the command
        :param additional_dependencies: additional dependencies needed by this command.
        :return:
        """
        logger.debug('_Initialize Command')
        self.name = identifier or self.default_identifier
        self.description = name or self.default_name

        if additional_dependencies is not None:
            self.dependencies = self.default_dependencies.union(additional_dependencies)

    def plugin_init(self):
        """
        Required to further initialize the plugin.
        :return:
        """
        self.xmpp.add_event_handler('session_start', self._start)

    def post_init(self):
        super(BaseCommand, self).post_init()
        self._forms = self.xmpp['xep_0004']
        self._roster = self.xmpp['rho_bot_roster']

    def _start(self, event):
        """
        Configure the command to be added to the list of commands supported by the bot.
        :return:
        """
        logger.info('Registering new command: %s' % self.name)
        self.xmpp['xep_0050'].add_command(node=self.name, name=self.description, handler=self._starting_point)

    def _starting_point(self, request, initial_session):
        """
        Starting point for the commands which will call command_start which should be overridden.
        :param request:
        :param initial_session:
        :return:
        """
        logger.info('_starting point')
        return self.command_start(request, initial_session)

    def command_start(self, request, initial_session):
        """
        Command starting point.
        :param request:
        :param initial_session:
        :return:
        """
        raise NotImplementedError()

    def get_command_uri(self):
        """
        Return the URI of this command so that it can be sent to other clients for lookups.
        :return:
        """
        jid = self._roster.get_jid()

        return "xmpp:%s?command;node=%s" % (jid, self.name)
