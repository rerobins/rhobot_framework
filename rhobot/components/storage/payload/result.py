"""
Payload for passing around results of commands.  In most cases this is a list of the nodes that were interacted with.
"""
from rdflib.namespace import RDF, RDFS
import logging

logger = logging.getLogger(__name__)

class ResultPayload:

    def __init__(self, about=None, types=None):

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
        return self._types


class ResultCollectionPayload:

    def __init__(self, container):
        self._container = container
        self._results = []
        self._unpack_container()

    def append(self, result):
        self._results.append(result)

    def _unpack_container(self):
        self._results = []

        for item in self._container.get_items():
            logger.info('item: %s' % item)
            result_payload = ResultPayload(about=item[str(RDF.about)], types=item[str(RDF.type)])
            self.append(result_payload)

    def populate_payload(self):
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
        return self._results
