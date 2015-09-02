"""
Payload for passing around results of commands.  In most cases this is a list of the nodes that were interacted with.
"""
from sleekxmpp.plugins.xep_0004 import Form
from rdflib.namespace import RDF
import logging
import json

logger = logging.getLogger(__name__)

FLAG_KEY = 'flags'


class ResultPayload:
    """
    Payload that contains basic details about a node from the client operations.  Contains the about which the URI for
    the node, and the types associated with that node.
    """

    def __init__(self, about=None, types=None, flags=None):
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

        self._flags = dict()

        if flags:
            if isinstance(flags, dict):
                for key, value in flags.iteritems():
                    self.add_flag(key, value)
            elif isinstance(flags, basestring):
                self._flags = json.loads(flags)

    def add_type(self, *args):
        """
        Add a list of types to the container.
        :param args:
        :return:
        """
        for arg in args:
            self._types.append(str(arg))

    def add_flag(self, key, value):
        """
        Add a flag key and value.
        :param key: key
        :param value: value.
        :return:
        """
        flag_values = self._flags.get(str(key), [])

        if isinstance(value, list):
            for val in value:
                flag_values.append(str(val))
        else:
            flag_values.append(str(value))

        self._flags[str(key)] = flag_values

    @property
    def types(self):
        """
        Retrieve the types associated with this result payload.
        :return: list of types.
        """
        return self._types

    @property
    def flags(self):
        """
        Retrieve the flags associated with this result payload.
        """
        return self._flags

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

    def append(self, *args):
        """
        Append a result to the collection.
        :param result:
        :return:
        """
        self._results += args

    def _unpack_container(self):
        """
        Unpack the container into the internal data structures.
        """
        self._results = []

        for item in self._container.get_items():
            logger.debug('item: %s' % item)
            about = None
            types = None
            flags = dict()

            for key, value in item.iteritems():
                if key == str(RDF.about):
                    about = value
                elif key == str(RDF.type):
                    types = value
                else:
                    flags[key] = value

            result_payload = ResultPayload(about=about, types=types, flags=flags)
            self.append(result_payload)

    def populate_payload(self):
        """
        Populate the data structures into the container for this object, and return it.
        :return: transmittable data structure.
        """
        self._container.clear()

        self._container.add_reported(var=str(RDF.about), ftype=str(RDF.about))
        self._container.add_reported(var=str(RDF.type), ftype=str(RDF.type))

        additional_flags = set()
        for result in self._results:
            additional_flags.update(result.flags.keys())

        for flag_value in additional_flags:
            self._container.add_reported(var=flag_value, ftype='text-multi')

        for result in self._results:
            parameters = {
                str(RDF.about): str(result.about),
                str(RDF.type): result.types
            }
            parameters.update(result.flags)

            self._container.add_item(parameters)

        return self._container

    @property
    def results(self):
        """
        Retrieve the results.
        :return: list of result payloads
        """
        return self._results
