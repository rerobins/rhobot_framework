"""
Executable script that will configure the application based on a python file that will be provided on the command line
arguments.
"""
import optparse
from rhobot import configuration
import logging

logger = logging.getLogger(__name__)

usage = 'usage: %prog [options] execution_file'
parser = optparse.OptionParser()
parser.add_option('-c', dest='filename', help='Configuration file for the bot', default='configuration')
(options, args) = parser.parse_args()

# Load the configuration details from the parser
print 'Loading configuration file: %s' % options.filename
configuration.load_file(options.filename)

# Find the application object from the overridden load script.
if len(args) != 1:
    parser.error('Must provide a execution file to load.')

# Load the execution file.
file_pointer = open(args[0])

variables = {'__file__': args[0], }

exec file_pointer in variables, variables

# See if there is an application value from that script.
if 'application' not in variables:
    parser.error('Execution file does not provide an application variable')

application = variables['application']

application.run()

# Connect to the XMPP server and start processing XMPP stanzas.
if application.bot.connect():
    application.bot.process(block=True)
else:
    print('Unable to connect.')
