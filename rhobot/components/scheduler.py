"""
Wraps scheduling functionality.
"""
from sleekxmpp.plugins.base import base_plugin
import uuid
import logging

logger = logging.getLogger(__name__)

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

class Deferred:

    def __init__(self, method_call, scheduler, promise=None):
        self._method_call = method_call
        if promise:
            self._promise = promise
        else:
            self._promise = Promise(scheduler)

    def promise(self):
        return self._promise

    def __call__(self, *args, **kwargs):
        logger.info('Executing call method')

        try:
            result = self._method_call()
            try:
                result.then(_generate_promise_fulfilled_ripple(self._promise),
                            _generate_promise_rejected_ripple(self._promise))
            except AttributeError:
                self._promise.resolved(result)
        except DeprecationWarning as e:
            logger.info('Rejecting promise')
            self._promise.rejected(e)

def _generate_promise_fulfilled_ripple(child_promise):

    def fulfilled(result):
        child_promise.resolved(result)

    return fulfilled

def _generate_promise_rejected_ripple(child_promise):

    def rejected(error):
        child_promise.rejected(error)

    return rejected


class Promise:

    def __init__(self, scheduler):

        self._queue = []

        self._result = None
        self._error = None
        self._scheduler = scheduler
        self._child_promise = None

    def then(self, fulfilled=None, rejected=None):

        new_promise = Promise(self._scheduler)

        # If the promise hasn't been resolved, add it to the queue, otherwise fire off the new deferred.
        if not(self._result or self._error):
            self._queue.append((fulfilled, rejected, new_promise))
        elif self._result:
            if fulfilled:
                deferred = Deferred(lambda: fulfilled(self._result), self._scheduler, new_promise)
                self._scheduler.schedule_task(deferred, delay=0.0)
        elif self._error:
            if rejected:
                self._scheduler.schedule_task(lambda: rejected(self._error), delay=0.0)
            self._scheduler.schedule_task(lambda: new_promise.rejected(self._error), delay=0.0)

        return new_promise

    def resolved(self, result):
        if not (self._result or self._error):
            self._result = result

            # schedule the fulfilled method call.

            for fulfilled, rejected, promise in self._queue:
                if fulfilled:
                    deferred = Deferred(lambda: fulfilled(self._result), self._scheduler, promise)
                    self._scheduler.schedule_task(deferred, delay=0.0)
                else:
                    self._scheduler.schedule_task(lambda: promise.resolved(self._result), delay=0.0)
        else:
            pass

        self._queue = None

    def rejected(self, error):
        if not (self._result or self._error):
            self._error = error
            # schedule the rejected method call
            for fulfilled, rejected, promise in self._queue:
                if rejected:
                    self._scheduler.schedule_task(lambda: rejected(self._error), delay=0.0)
                self._scheduler.schedule_task(lambda: promise.rejected(self._error), delay=0.0)
        else:
            pass

        self._queue = None


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

    def defer(self, method, *args, **kwargs):
        deferred = Deferred(method, self)

        logger.info('Scheduling task')
        self.schedule_task(deferred, delay=0.0)

        logger.info('Returning promise')
        return deferred.promise()

    def promise(self):
        return Promise(self)


# Define the plugin that will be used to access this plugin.
rho_bot_scheduler = Scheduler
