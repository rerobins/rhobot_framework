"""
Namespaces that are going to be used for working with the storage client.
"""
from rdflib.namespace import ClosedNamespace


NEO4J = ClosedNamespace(uri='http://www.neo4j.com/terms/#',
                        terms=['cypher'])
