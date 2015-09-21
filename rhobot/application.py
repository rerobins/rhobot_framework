"""
Provide a framework entry point for this architecture.  This should alleviate some of the duplicate code from the
sub applications.
"""
import logging
from rhobot.bot import RhoBot

logger = logging.getLogger(__name__)


class Application:
    """
    Application entry point for the bots.
    """

    def __init__(self):
        self._pre_initialization = []
        self._post_initialization = []
        self._bot = None

    def pre_init(self, func):
        """
        Decorator that will register a method to be executed before the rhobot framework has been initialized.
        :param func: function to execute.
        :return:
        """
        self._pre_initialization.append(func)
        return func

    def post_init(self, func):
        """
        Decorator that will register a method to be executed after the rhobot framework has been initialized.
        :param func: function to execute.
        :return:
        """
        self._post_initialization.append(func)
        return func

    def run(self):
        """
        This method will execute the framework.  It should only be executed by the framework code.
        :return:
        """

        for method in self._pre_initialization:
            try:
                method()
            except Exception as e:
                logger.error('Error executing method: %s' % method.__name__)
                raise e

        self._bot = RhoBot()

        for method in self._post_initialization:
            try:
                method(self._bot)
            except Exception as e:
                logger.error('Error executing post_initialization method: %s' % method.__name__)
                raise e

    @property
    def bot(self):
        return self._bot
