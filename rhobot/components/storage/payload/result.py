"""
Payload for passing around results of commands.  In most cases this is a list of the nodes that were interacted with.
"""
from sleekxmpp.plugins.xep_0004 import Form, FormField
from rdflib.namespace import RDF, RDFS
from rhobot.components.stanzas.rdf_stanza import RDFType
from rhobot.components.storage.enums import Flag
import logging

logger = logging.getLogger(__name__)

class _ColumnKey:

    def __init__(self, key, data_type):
        self._key = key
        self._type = str(data_type)
        self._hash = hash(self._key + ":" + self._type)

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return self._key == other.key and self._type == other.data_type

    def __cmp__(self, other):
        if self._key == other.key:
            return cmp(self._type, other.data_type)
        else:
            return cmp(self.key, other.key)

    @property
    def key(self):
        return self._key

    @property
    def data_type(self):
        return self._type


class ResultPayload:
    """
    Payload that contains basic details about a node from the client operations.  Contains the about which the URI for
    the node, and the types associated with that node.
    """

    def __init__(self, about=None, types=None, flags=None, columns=None):
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
        self._columns = dict()

        if flags:
            for key, value in flags.iteritems():
                self.add_flag(key, value)

        if columns:
            for key, value in columns.iteritems():
                self.add_column(key, value)

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
        self._flags[key] = value

    def add_column(self, key, value, data_type=RDFS.Literal):
        """
        Add a collection of columns to the key.
        :param key:
        :param value:
        :return:
        """
        column_key = _ColumnKey(key, data_type)
        column_values = self._columns.setdefault(column_key, [])

        if isinstance(value, list):
            value = [str(val) for val in value]
        else:
            value = [str(value)]

        column_values += value

    def get_column(self, key, data_type=RDFS.Literal):
        column_key = _ColumnKey(key, data_type)

        return self._columns.get(column_key, [])

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

    @property
    def columns(self):
        """
        Retrieve the columns associated with this result payload.
        """
        return self._columns


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

        reported_values = self._container.get_reported()

        for item in self._container.get_items():
            logger.debug('item: %s' % item)
            about = None
            types = None
            flags = dict()
            columns = dict()

            for key, value in item.iteritems():
                if key == str(RDF.about):
                    about = value
                elif key == str(RDF.type):
                    types = value
                else:
                    reported_item = reported_values[key]
                    if reported_item['rdftype']['type']:
                        columns[_ColumnKey(key, reported_item['rdftype']['type'])] = value
                    else:
                        flags[Flag(*(key, reported_item['type'], None))] = value

            result_payload = ResultPayload(about=about, types=types)
            for key, value in flags.iteritems():
                result_payload.add_flag(key, value)

            for key, value in columns.iteritems():
                result_payload.add_column(key.key, value, key.data_type)

            self.append(result_payload)

    def populate_payload(self):
        """
        Populate the data structures into the container for this object, and return it.
        :return: transmittable data structure.
        """
        self._container.clear()

        self._container.add_reported(var=str(RDF.about), ftype='list-multi')
        self._container.add_reported(var=str(RDF.type), ftype='list-multi')

        additional_flags = set()
        additional_columns = set()
        for result in self._results:
            additional_flags.update(result.flags.keys())
            additional_columns.update(result.columns.keys())

        for flag_value in additional_flags:
            self._container.add_reported(var=flag_value.var, ftype=flag_value.field_type)

        for column_value in additional_columns:
            reported = self._container.add_reported(var=column_value.key, ftype='list-multi')
            rdf_type = RDFType()
            rdf_type['type'] = column_value.data_type
            reported.append(rdf_type)

        for result in self._results:
            parameters = {
                str(RDF.about): str(result.about),
                str(RDF.type): result.types
            }

            for key, value in result.flags.iteritems():
                parameters[key.var] = value

            for key, value in result.columns.iteritems():
                parameters[key.key] = value

            self._container.add_item(parameters)

        return self._container

    @property
    def results(self):
        """
        Retrieve the results.
        :return: list of result payloads
        """
        return self._results
