from rhobot.components.commands.base_command import BaseCommand
import logging

logger = logging.getLogger(__name__)


class ResetConfiguration(BaseCommand):
    """
    Command that will reset the configuration details of the bot.
    """

    name = 'reset_configuration'
    description = 'Reset Configuration'
    dependencies = BaseCommand.default_dependencies.union(({'rho_bot_configuration', }))

    def post_init(self):
        self._configuration = self.xmpp['rho_bot_configuration']

    def command_start(self, request, initial_session):
        """
        Start the command.
        :param request:
        :param initial_session:
        :return:
        """
        form = self._forms.make_form()

        form.add_field(var='login', ftype='fixed', label='Access Login',
                       desc='Authorization URL',
                       required=True,
                       value='Are you sure you want to reset configuration?')

        initial_session['payload'] = form
        initial_session['next'] = self.reset_configuration
        initial_session['has_next'] = False

        return initial_session

    def reset_configuration(self, request, session):
        """
        Clear out the configuration details.
        :param request:
        :param session:
        :return:
        """
        configuration = self._configuration.get_configuration()
        configuration.clear()

        self._configuration.store_data()

        session['payload'] = None

        return session

reset_configuration = ResetConfiguration
