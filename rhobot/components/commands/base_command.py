import logging
from sleekxmpp.plugins.base import base_plugin

logger = logging.getLogger(__name__)


class BaseCommand(base_plugin):
    """
    Abstract implementation of a base command.
    """

    default_dependencies = {'xep_0050', 'rho_bot_roster', }

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
        self._commands = self.xmpp['xep_0050']

    def _start(self, event):
        """
        Configure the command to be added to the list of commands supported by the bot.
        :return:
        """
        self._commands.add_command(node=self.name, name=self.description, handler=self._starting_point)

    def _starting_point(self, request, initial_session):
        """
        Starting point for the commands which will call command_start which should be overridden.
        :param request:
        :param initial_session:
        :return:
        """
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
