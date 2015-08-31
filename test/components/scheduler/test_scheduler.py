from sleekxmpp.test import SleekTest
import unittest
import mock
import time

class SchedulerTester(SleekTest):

    def tearDown(self):
        self.stream_close()

    def test_simple_schedule(self):

        self.stream_start(plugins=[])

        self.xmpp.register_plugin('rho_bot_scheduler', module='rhobot.components')

        callback = mock.MagicMock()
        delay = 0.0

        self.xmpp['rho_bot_scheduler'].schedule_task(callback, delay=delay)

        time.sleep(delay + 0.1)

        self.assertEqual(callback.call_count, 1)

    def test_cancel(self):

        self.stream_start(plugins=[])

        self.xmpp.register_plugin('rho_bot_scheduler', module='rhobot.components')

        callback = mock.MagicMock()
        delay = 4.0

        cancel_handler = self.xmpp['rho_bot_scheduler'].schedule_task(callback, delay=delay)

        time.sleep(delay/2)

        cancel_handler()

        time.sleep(delay + 1)

        self.assertEqual(callback.call_count, 0)

    def test_defer(self):

        self.stream_start(plugins=[])
        self.xmpp.register_plugin('rho_bot_scheduler', module='rhobot.components')

        return_value = 'return_value'

        callback = mock.Mock()
        callback.return_value = return_value

        promise_result = mock.Mock()

        promise = self.xmpp['rho_bot_scheduler'].defer(callback).then(promise_result)

        time.sleep(1.0)

        self.assertEqual(callback.call_count, 1)
        self.assertEqual(promise_result.call_count, 1)

        args, kwargs = promise_result.call_args
        self.assertEqual(args[0], return_value)


suite = unittest.TestLoader().loadTestsFromTestCase(SchedulerTester)
