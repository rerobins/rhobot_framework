"""
Helper that will attempt to get a node from the database.  If it doesn't exist in the database, it will attempt to
look it up through the rdf publisher.
"""
from sleekxmpp.plugins.base import base_plugin
from rhobot.components.storage import StoragePayload
from rdflib.namespace import RDFS


class GetOrLookup(base_plugin):
    """
    This will create a callable that will handle a bulk of the heavy lifting for get or lookup.
    """

    name = 'rho_bot_get_or_lookup'
    dependencies = {'rho_bot_rdf_publish', 'rho_bot_storage_client', }
    description = 'RHO: Get or Lookup Plugin'

    def plugin_init(self):
        pass

    def post_init(self):
        self._rdf_publish = self.xmpp['rho_bot_rdf_publish']
        self._storage_client = self.xmpp['rho_bot_storage_client']
        self._scheduler = self.xmpp['rho_bot_scheduler']

    def __call__(self, payload, *args, **kwargs):
        """
        Call the callable.
        :param payload: payload
        :param args:
        :param kwargs:
        :return: promise that will return a storage payload that will contain details about the look up.
        """
        return self._storage_client.get_node(payload).then(
            self._scheduler.generate_promise_handler(self._process_lookup_result, payload))

    def _process_lookup_result(self, result, payload):
        """
        This will split the promise chain in two.  If the result returns a value, then the promise will drop off.  If
        the result doesn't exist, then do an rdf publish and return the result of that.
        :param result: the result of the get_command.
        :param payload: the payload that was used to look up the data.
        :return: a value or a promise that will return the value.
        """
        if result.about:
            return result.about

        location_request = StoragePayload()
        location_request.add_type(*payload.types)
        location_request.add_property(RDFS.seeAlso, payload.about)

        promise = self._rdf_publish.send_out_request(location_request)
        promise.then(self._lookup_handler)

        return promise

    def _lookup_handler(self, results_container):
        """
        Handle the rdf publish look up value by processing the results.
        :param results_container: the container that was returned by the lookup request.
        :return:
        """
        if results_container.results:
            return results_container.results[0].about

        raise RuntimeError('No results returned from look up')

rho_bot_get_or_lookup = GetOrLookup
