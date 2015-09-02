"""
Enumerated values for working with the storage implementations.
"""
from enum import Enum, unique
from rdflib.namespace import RDF
import json


class _FlagMixin:

    def get_value(self, flags):

        value = self.value

        key = value['var']
        default = value['default']

        value = flags.get(key, default)

        if isinstance(value, list) and len(value) == 1:
            value = value[0]

        return value


@unique
class Commands(Enum):
    CREATE_NODE = 'create_node'
    UPDATE_NODE = 'update_node'
    DELETE_NODE = 'delete_node'
    FIND_NODE = 'find_node'
    GET_NODE = 'get_node'
    CYPHER = 'cypher'


@unique
class UpdateFlags(Enum):
    # Should the node have it's data removed before the new data is inserted into the data.  This should be a boolean.
    CLEAR_NODE_BEFORE_WRITE = dict(var='clear_node_before_write', type='boolean', default=False)

    # Should replace the currently defined values in the node with the values in the payload.  Does not modify any
    # fields that are not defined in the payload.
    REPLACE_DEFINED = dict(var='replace_defined', type='boolean', default=False)


@unique
class FindFlags(Enum):
    # Should the node be created if it isn't found.  This should be a boolean.
    CREATE_IF_MISSING = dict(var='create_if_missing', type='boolean', default=False)


@unique
class FindResults(Enum):
    # Was the node created when it was found. This should return a boolean.
    CREATED = 'created'


@unique
class CypherFlags(_FlagMixin, Enum):
    TRANSLATION_KEY = dict(var='translation_key', type='text-single',
                           default=json.dumps({str(RDF.about): 'node'}))
