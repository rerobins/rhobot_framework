"""
Enumerated values for working with the storage implementations.
"""
from enum import Enum, unique

@unique
class Commands(Enum):
    CREATE_NODE = 'create_node'
    UPDATE_NODE = 'update_node'
    DELETE_NODE = 'delete_node'
    FIND_NODE = 'find_node'


@unique
class UpdateFlags(Enum):
    # Should the node have it's data removed before the new data is inserted into the data.  This should be a boolean.
    CLEAR_NODE_BEFORE_WRITE = dict(var='clear_node_before_write', type='boolean', default=False)

@unique
class FindFlags(Enum):
    # Should the node be created if it isn't found.  This should be a boolean.
    CREATE_IF_MISSING = dict(var='create_if_missing', type='boolean', default=False)
