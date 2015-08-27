"""
Payload for passing around results of commands.  In most cases this is a list of the nodes that were interacted with.
"""
from sleekxmpp.plugins.xep_0004 import Form
from rdflib.namespace import RDF, RDFS
import logging

logger = logging.getLogger(__name__)

class ResultPayload:
    """
    Payload that contains basic details about a node from the client operations.  Contains the about which the URI for
    the node, and the types associated with that node.
    """

    def __init__(self, about=None, types=None):
        """
        Constructor.
        :param about: about value
        :param types: list of types
        :return:
        """
        self._types = []
        if types:
            if isinstance(types, basestring):
                types = [types]
            self.add_type(*types)
        self.about = about

    def add_type(self, *args):
        """
        Add a list of types to the container.
        :param args:
        :return:
        """
        for arg in args:
            self._types.append(str(arg))

    def types(self):
        """
        Retrieve the types associated with this result payload.
        :return: list of types.
        """
        return self._types


class ResultCollectionPayload:
    """
    Collection of result payloads.
    """

    def __init__(self, container=None):
        """
        Constructor.
        :param container: optional container to populate values from.
        """
        self._results = []

        if not container:
            self._container = Form()
        else:
            self._container = container
            self._unpack_container()

    def append(self, result):
        """
        Append a result to the collection.
        :param result:
        :return:
        """
        self._results.append(result)

    def _unpack_container(self):
        """
        Unpack the container into the internal data structures.
        """
        self._results = []

        for item in self._container.get_items():
            logger.info('item: %s' % item)
            result_payload = ResultPayload(about=item[str(RDF.about)], types=item[str(RDF.type)])
            self.append(result_payload)

    def populate_payload(self):
        """
        Populate the data structures into the container for this object, and return it.
        :return: transmittable data structure.
        """
        self._container.clear()

        self._container.add_reported(var=str(RDF.about), ftype=str(RDFS.Literal))
        self._container.add_reported(var=str(RDF.type), ftype=str(RDF.type))

        for result in self._results:
            parameters = {
                str(RDF.about): str(result.about),
                str(RDF.type): result.types()
            }
            self._container.add_item(parameters)

        return self._container

    def results(self):
        """
        Retrieve the results.
        :return: list of result payloads
        """
        return self._results
