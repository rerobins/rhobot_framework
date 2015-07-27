"""
This will modify the form stanzas so that it can handle more RDF information.
"""
from sleekxmpp.plugins.xep_0004.stanza import FormField, Form
from rdflib.namespace import RDFS, RDF


def patch_form_fields():
    FormField.multi_value_types.add(RDFS.Resource.toPython())
    FormField.multi_value_types.add(RDFS.Literal.toPython())
    FormField.multi_value_types.add(RDF.type.toPython())

if __name__ == '__main__':
    from rdflib.namespace import FOAF

    patch_form_fields()

    f = FormField()

    f.set_type(RDFS.Resource.toPython())
    f.set_value(['http://some_url.com', 'htpp://someothervalue.com'])

    print '%s' % f

    form = Form(title='Some Form')
    form.set_type('result')

    form.add_field(var=FOAF.knows.toPython(),
                   value=['http://some_url.com', 'http://someother_vlaue.com'],
                   ftype=RDFS.Resource.toPython())

    print '%s' % form
