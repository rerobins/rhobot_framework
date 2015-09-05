"""
Enumerated values for working with the storage implementations.
"""
from sleekxmpp.plugins.xep_0004 import FormField
from enum import Enum, unique
from rdflib.namespace import RDF
import json


class Flag:
    """
    Mixin that will provide a means to retrieve the values from the data type.
    """

    def __init__(self, *args):

        if len(args) != 3:
            raise AttributeError('Flag Enumeration must be provided with 3 argument values.')

        self._var = args[0]
        self._field_type = args[1]
        self._default = args[2]

    @property
    def var(self):
        return self._var

    @property
    def field_type(self):
        return self._field_type

    @property
    def default(self):
        return self._default

    def fetch_from(self, dictionary):

        result = self._default

        if self in dictionary:
            result = dictionary[self]
        else:
            for var in [variable for variable in dictionary.keys() if variable.var == self.var]:
                result = dictionary[var]

        if result and self.field_type == 'boolean':
            result = result in FormField.true_values

        return result


@unique
class Commands(Enum):
    CREATE_NODE = 'create_node'
    UPDATE_NODE = 'update_node'
    DELETE_NODE = 'delete_node'
    FIND_NODE = 'find_node'
    GET_NODE = 'get_node'
    CYPHER = 'cypher'


@unique
class UpdateFlags(Flag, Enum):
    # Should the node have it's data removed before the new data is inserted into the data.  This should be a boolean.
    CLEAR_NODE_BEFORE_WRITE = ('clear_node_before_write', 'boolean', False)

    # Should replace the currently defined values in the node with the values in the payload.  Does not modify any
    # fields that are not defined in the payload.
    REPLACE_DEFINED = ('replace_defined', 'boolean', False)


@unique
class FindFlags(Flag, Enum):
    # Should the node be created if it isn't found.  This should be a boolean.
    CREATE_IF_MISSING = ('create_if_missing', 'boolean', False)


@unique
class FindResults(Flag, Enum):
    # Was the node created when it was found. This should return a boolean.
    CREATED = ('created', 'boolean', False)


@unique
class CypherFlags(Flag, Enum):
    TRANSLATION_KEY = ('translation_key', 'text-single', json.dumps({str(RDF.about): 'node'}))
