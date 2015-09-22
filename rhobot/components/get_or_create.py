"""
Get or create from the storage container.
"""
from sleekxmpp.plugins.base import base_plugin
from rhobot.components.storage import StoragePayload
from rdflib.namespace import DCTERMS


class GetOrCreate(base_plugin):
    """
    Callable plugin that will get or create a node in the database based on the storage payload provided.
    """
    name = 'rho_bot_get_or_create'
    description = 'Get or create plugin'
    dependencies = {'rho_bot_storage_client', 'rho_bot_scheduler', 'rho_bot_representation_manager',
                    'rho_bot_rdf_publish'}

    def plugin_init(self):
        """
        Initialize the plugin.
        :return:
        """

    def post_init(self):
        """
        Finish the plugin initialization.
        :return:
        """
        super(GetOrCreate, self).post_init()
        self._storage_client = self.xmpp['rho_bot_storage_client']
        self._scheduler = self.xmpp['rho_bot_scheduler']
        self._representation_manager = self.xmpp['rho_bot_representation_manager']
        self._rdf_publish = self.xmpp['rho_bot_rdf_publish']

    def __call__(self, storage_payload):
        """
        Call the get or create.
        :param storage_payload:
        :return:
        """
        promise = self._storage_client.find_nodes(storage_payload).then(self._handle_result)
        promise = promise.then(None,
                               self._scheduler.generate_promise_handler(self._create, storage_payload))
        promise = promise.then(self._get_node)

        return promise

    def _handle_result(self, result):
        """
        Process the result from the find_nodes.
        :param result:
        :return:
        """
        if not result.results:
            raise Exception('Result not found')

        return result.results[0].about

    def _create(self, error_message, storage_payload):
        """
        Create the node since it doesn't exist.
        :param error_message:
        :param storage_payload:
        :return:
        """
        def _handle_result(_result):
            # Publish the create event
            self._rdf_publish.publish_all_results(_result, created=True)

            return _result.results[0].about

        storage_payload.add_reference(DCTERMS.creator, self._representation_manager.representation_uri)

        return self._storage_client.create_node(storage_payload).then(_handle_result)

    def _get_node(self, uri):
        """
        Retrieve the actual node.
        :param uri:
        :return:
        """
        get_payload = StoragePayload()
        get_payload.about = uri

        return self._storage_client.get_node(get_payload)


rho_bot_get_or_create = GetOrCreate
