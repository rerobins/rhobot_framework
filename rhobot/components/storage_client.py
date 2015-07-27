"""
Module that will be used to help storage clients connect to a data store.
"""
import logging
from rdflib.namespace import FOAF, RDFS, RDF
from sleekxmpp.plugins.base import base_plugin


logger = logging.getLogger(__name__)

CREATE_NODE_COMMAND = 'create_node'


class StorageClient(base_plugin):

    name = 'rho_bot_storage_client'
    dependencies = {'rho_bot_roster', 'xep_0050'}
    description = 'Storage Client Plugin'

    def plugin_init(self):
        self._storage_jid = None
        pass

    def post_init(self):
        self.xmpp.add_event_handler('online:store', self._store_found)

    def _store_found(self, data):
        logger.info('Found a store: %s' % data)
        self._storage_jid = data
        self.xmpp.schedule('test_store', 1.0, self._test_store)

    def _test_store(self):
        logger.info('Attempting a test store message')

        form = self.xmpp['xep_0004'].make_form()
        form.set_type('result')

        form.add_field(var=RDF.type.toPython(),
                       value=[FOAF.Person.toPython()],
                       ftype=RDF.type.toPython())
        form.add_field(var=FOAF.knows.toPython(),
                       value=['http://some_url.com', 'http://someother_vlaue.com'],
                       ftype=RDFS.Literal.toPython())
        form.add_field(var=FOAF.familyName.toPython(),
                       value='Robinson',
                       ftype=RDFS.Literal.toPython())

        session = dict(next=self._store_result,
                       error=self._store_error,
                       payload=[form])

        self.xmpp['xep_0050'].start_command(jid=self._storage_jid, node=CREATE_NODE_COMMAND, session=session)

    def _store_result(self, iq, session):
        logger.info('Store Result iq: %s' % iq)
        logger.info('Store Result session: %s' % session)

    def _store_error(self, iq, session):
        logger.info('Store Error iq: %s' % iq)
        logger.info('Store Error session: %s' % session)

rho_bot_storage_client = StorageClient
