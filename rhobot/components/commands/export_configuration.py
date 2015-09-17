"""
This is a command that will export the configuration details for debugging.  This command should only be available when
the bot is in a debug mode.

The exported file format will be JSON.
"""

from rhobot.components.commands.base_command import BaseCommand
import logging
import json

logger = logging.getLogger(__name__)


class ExportConfiguration(BaseCommand):

    name = 'export_configuration'
    description = 'Export Configuration'
    dependencies = BaseCommand.default_dependencies.union({'rho_bot_configuration', })

    def command_start(self, request, initial_session):
        """
        Provide the configuration details back to the requester and end the command.
        :param request:
        :param initial_session:
        :return:
        """
        configuration_object = self.xmpp['rho_bot_configuration'].get_configuration()

        configuration_string = json.dumps(configuration_object)

        form = self.xmpp['xep_0004'].make_form(ftype='result')

        form.add_reported(var='content', ftype='text-multi', label='Content')

        form.add_item({'content': configuration_string})

        initial_session['payload'] = form
        initial_session['next'] = None
        initial_session['has_next'] = False
        initial_session['notes'] = (('info', "Here is the current configuration for the bot."),)

        return initial_session

export_configuration = ExportConfiguration
