from rhobot.components.commands.base_command import BaseCommand
import logging

logger = logging.getLogger(__name__)


class ResetConfiguration(BaseCommand):
    """
    Command that will reset the configuration details of the bot.
    """

    def initialize_command(self):
        logger.info('Initialize Command')
        self._initialize_command(identifier='reset_configuration', name='Reset Configuration',
                                 additional_dependencies={'rho_bot_configuration'})

    def command_start(self, request, initial_session):
        """
        Start the command.
        :param request:
        :param initial_session:
        :return:
        """
        form = self.xmpp['xep_0004'].make_form()

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
        logger.info('Reset Configuration')
        configuration = self.xmpp['rho_bot_configuration'].get_configuration()
        configuration.clear()

        self.xmpp['rho_bot_configuration'].store_data()

        return session

reset_configuration = ResetConfiguration
