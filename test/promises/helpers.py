from sleekxmpp.test import SleekTest
import threading

def generate_fulfilled_test_case(method, value):

    class TestFulfilled(SleekTest):

        def __init__(self, *args, **kwargs):
            super(TestFulfilled, self).__init__(*args, **kwargs)
            self._test_case = method

        def setUp(self):
            self.session = {}
            self.stream_start(plugins=[])
            self.xmpp.register_plugin('rho_bot_scheduler', module='rhobot.components')
            self.scheduler = self.xmpp['rho_bot_scheduler']

        def tearDown(self):
            self.stream_close()

        def _generate_done(self, event):

            def done():
                event.set()

            return done

        def test_already_fulfilled(self):

            if not self.scheduler:
                raise NotImplementedError('Scheduler is not defined')

            test = self._test_case

            event = threading.Event()
            promise = self.scheduler.promise()
            promise.resolved(value)
            test(self, promise, self._generate_done(event))

            self.assertTrue(event.wait(1.0))

        def test_fulfilled_immediately(self):

            if not self.scheduler:
                raise NotImplementedError('Scheduler is not defined')

            test = self._test_case

            event = threading.Event()
            promise = self.scheduler.promise()

            test(self, promise, self._generate_done(event))
            promise.resolved(value)

            self.assertTrue(event.wait(10.0))

        def test_fulfilled_eventually(self):

            if not self.scheduler:
                raise NotImplementedError('Scheduler is not defined')

            test = self._test_case

            event = threading.Event()
            promise = self.scheduler.promise()

            test(self, promise, self._generate_done(event))

            self.scheduler.schedule_task(lambda: promise.resolved(value), delay=0.050)

            self.assertTrue(event.wait(10.0))

    return TestFulfilled


def generate_rejected_test_case(method, value):

    class TestRejected(SleekTest):

        def __init__(self, *args, **kwargs):
            super(TestRejected, self).__init__(*args, **kwargs)
            self._test_case = method

        def setUp(self):
            self.session = {}
            self.stream_start(plugins=[])
            self.xmpp.register_plugin('rho_bot_scheduler', module='rhobot.components')
            self.scheduler = self.xmpp['rho_bot_scheduler']

        def tearDown(self):
            self.stream_close()

        def _generate_done(self, event):

            def done():
                event.set()

            return done

        def test_already_rejected(self):

            if not self.scheduler:
                raise NotImplementedError('Scheduler is not defined')

            test = self._test_case

            event = threading.Event()
            promise = self.scheduler.promise()
            promise.rejected(value)
            test(self, promise, self._generate_done(event))

            self.assertTrue(event.wait(1.0))

        def test_rejected_immediately(self):

            if not self.scheduler:
                raise NotImplementedError('Scheduler is not defined')

            test = self._test_case

            event = threading.Event()
            promise = self.scheduler.promise()

            test(self, promise, self._generate_done(event))
            promise.rejected(value)

            self.assertTrue(event.wait(10.0))

        def test_rejected_eventually(self):

            if not self.scheduler:
                raise NotImplementedError('Scheduler is not defined')

            test = self._test_case

            event = threading.Event()
            promise = self.scheduler.promise()

            test(self, promise, self._generate_done(event))

            self.scheduler.schedule_task(lambda: promise.rejected(value), delay=0.050)

            self.assertTrue(event.wait(10.0))

    return TestRejected

