"""
This command will import a provided json data structure into the configuration object of the bot.  It will clear away
the current configuration.
"""

from rhobot.components.commands.base_command import BaseCommand
import logging
import json

logger = logging.getLogger(__name__)


class ImportConfiguration(BaseCommand):

    def initialize_command(self):
        super(ImportConfiguration, self).initialize_command()

        logger.info('Initialize Command')
        self._initialize_command(identifier='import_configuration', name='Import Configuration',
                                 additional_dependencies={'rho_bot_configuration'})

    def command_start(self, request, initial_session):
        """
        Provide the configuration details back to the requester and end the command.
        :param request:
        :param initial_session:
        :return:
        """
        configuration_object = self.xmpp['rho_bot_configuration'].get_configuration()

        configuration_string = json.dumps(configuration_object)

        form = self.xmpp['xep_0004'].make_form(ftype='form')

        form.add_field(var='content', ftype='text-multi', label='Content', value=configuration_string)

        initial_session['payload'] = form
        initial_session['next'] = self.store_results
        initial_session['has_next'] = False

        return initial_session

    def store_results(self, request, session):

        configuration_dictionary = json.loads(request['values']['content'])

        configuration_object = self.xmpp['rho_bot_configuration'].get_configuration()
        configuration_object.clear()

        configuration_object.update(configuration_dictionary)

        self.xmpp['rho_bot_configuration'].store_data()

        session['notes'] = (('info', 'Results imported to database',),)
        session['has_next'] = False
        session['next'] = None

        return session


import_configuration = ImportConfiguration
