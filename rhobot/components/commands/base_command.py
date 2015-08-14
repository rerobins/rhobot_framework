import logging
from sleekxmpp.plugins.base import base_plugin

logger = logging.getLogger(__name__)

class BaseCommand(base_plugin):
    """
    Abstract implementation of a base command.
    """

    default_identifier = 'base_command_identifier'
    default_name = 'Base Command Name'
    default_dependencies = {'xep_0050', }

    def __init__(self, xmpp, config):
        base_plugin.__init__(self, xmpp, config=config)
        self.initialize_command()

    def initialize_command(self):
        """
        Initialize the command.
        :return:
        """
        logger.info('Initialize Command')
        self._initialize_command(self.default_identifier, self.default_name, {})

    def _initialize_command(self, identifier, name, additional_dependencies=None):
        """
        Initialization of the command.
        :param identifier: identifier that will be used to determine how other bots reference this command.
        :param name: human readable name of the command
        :param additional_dependencies: additional dependencies needed by this command.
        :return:
        """
        logger.info('_Initialize Command')
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
