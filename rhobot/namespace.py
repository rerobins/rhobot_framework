from rdflib.namespace import ClosedNamespace, Namespace

RHO = ClosedNamespace(uri='urn:rho:', terms=['Owner'])

#: Namespace for working with events.
EVENT = Namespace('http://purl.org/NET/c4dm/event.owl#')

#: Namespace for working with schema.org data types
SCHEMA = Namespace('http://schema.org/')

#: Namespace for working with WGS84 data types
WGS_84 = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')

#: Namespace for working with location data types
LOCATION = Namespace('http://www.w3.org/ns/locn#')

#: Namespace for working with graph data types.
GRAPH = ClosedNamespace(uri='urn:graph:', terms=['degree'])

#: Namespace for working with intervals
TIMELINE = Namespace('http://purl.org/NET/c4dm/timeline.owl#')
