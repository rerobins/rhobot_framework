from rhobot.components.scheduler import rho_bot_scheduler
from rhobot.components.configuration import rho_bot_configuration
from rhobot.components.roster import rho_bot_roster
from rhobot.components.storage.client import rho_bot_storage_client
from rhobot.components.rdf_publish import rho_bot_rdf_publish
from rhobot.components.representation_manager import rho_bot_representation_manager
from rhobot.components.commands import export_configuration, import_configuration, reset_configuration

from sleekxmpp.plugins.base import register_plugin

def register_core_plugins():
    """
    Register the core plugins for the system.
    :return: None
    """
    register_plugin(rho_bot_scheduler)
    register_plugin(rho_bot_configuration)
    register_plugin(rho_bot_roster)
    register_plugin(rho_bot_storage_client)
    register_plugin(rho_bot_rdf_publish)
    register_plugin(rho_bot_representation_manager)
    register_plugin(export_configuration)
    register_plugin(import_configuration)
    register_plugin(reset_configuration)
