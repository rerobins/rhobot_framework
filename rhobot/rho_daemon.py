"""
Daemon execution script.
"""
from daemon import runner
import os
import lockfile
import grp
import logging
import logging.config
import json
from rhobot import configuration


# Configure all of the logging.
if os.path.exists('logging.json'):
    with open('logging.json', 'rt') as f:
        config = json.load(f)
        logging.config.dictConfig(config)
else:
    logging.basicConfig()

logger = logging.getLogger(__name__)

# Need to gather up a collection of parameters from the environment in order to configure this daemon.
working_directory = os.environ.get('WORKING_DIRECTORY', os.getcwd())
execution_file = os.environ.get('EXECUTION_FILE', '')
configuration_file = os.environ.get('CONFIGURATION_FILE', os.path.join(working_directory, 'configuration'))
pid_file = os.environ.get('PID_FILE', os.path.join(working_directory, 'rho.pid'))
uid = ''
gid = ''

class App:
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  pid_file
        self.pidfile_timeout = 5

        # Configure the application from the execution file
        execution_fp = open(execution_file)
        variables = {'__file__': execution_file}

        exec execution_fp in variables, variables

        if 'application' not in variables:
            logger.error('variable application not defined in %s' % execution_file)
            exit(-1)

        logger.info('application found')

        self._application = variables['application']
        self._application.run()

    def run(self):
        logger.info('connect...')
        if self._application.bot.connect():
            logger.info('start processing')
            self._application.bot.process(block=True)
        else:
            logger.error('Unable to connect.')

        logger.info('context created')


logger.info('working_directory: %s' % working_directory)
logger.info('execution_file: %s' % execution_file)
logger.info('configuration_file: %s' % configuration_file)
logger.info('pid_file: %s' % pid_file)

# Load configuration file
configuration.load_file(configuration_file)

app = App()

daemon_runner = runner.DaemonRunner(app)
daemon_runner.daemon_context.working_directory = working_directory


preserve_files = []
# Need to go through all of the logger handlers and add their files to the list of preservation files
for handler in logging._handlerList:
    logger.info('Iterating over handler: %s' % handler())
    if hasattr(handler(), 'baseFilename'):
        logger.info('Preserving: %s' % handler().baseFilename)
        preserve_files.append(handler().stream)

daemon_runner.daemon_context.files_preserve = preserve_files
daemon_runner.do_action()
