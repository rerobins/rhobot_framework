"""
This will modify the form stanzas so that it can handle more RDF information.
"""
from sleekxmpp.plugins.xep_0004.stanza import FormField
from rdflib.namespace import RDFS, RDF


def patch_form_fields():
    FormField.multi_value_types.add(RDFS.Resource.toPython())
    FormField.multi_value_types.add(RDFS.Literal.toPython())
    FormField.multi_value_types.add(RDF.type.toPython())
