"""
Wraps scheduling functionality.
"""
from sleekxmpp.plugins.base import base_plugin
import uuid

def _generate_cancel_method(scheduler_name, scheduler):
    """
    Handler that will be used to interact with the tasks that are going to be executed or not.
    """

    def cancel():
        """
        Cancel the task.
        :return:
        """
        scheduler.remove(scheduler_name)

    return cancel

class Scheduler(base_plugin):
    """
    Scheduler plugin that will wrap the scheduling functionality for the bots that are being defined.
    """

    name = 'rho_bot_scheduler'
    dependencies = {}
    description = 'Scheduling Plugin'

    def plugin_init(self):
        """
        Initialize the scheduler.
        :return:
        """

    def schedule_task(self, callback, delay=1.0, repeat=False, execute_now=False):
        """
        Schedule a task that is to be executed by the scheduling thread of the bot.
        :param callback: callback that is to be executed.
        :param delay: delay time that will be waited before executing
        :param repeat: should the task be repeated
        :param execute_now: execute the task immediately
        :return: cancel method
        """
        task_name = str(uuid.uuid4())

        self.xmpp.schedule(task_name, delay, callback, repeat=repeat)

        return _generate_cancel_method(task_name, self.xmpp.scheduler)


# Define the plugin that will be used to access this plugin.
rho_bot_scheduler = Scheduler
