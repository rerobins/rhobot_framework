"""
Verify that the stanza modification is working correctly.
"""
import unittest
from rhobot.stanza_modification import patch_form_fields
from rdflib.namespace import FOAF, RDFS
from sleekxmpp.plugins.xep_0004.stanza import Form, FormField


class StanzaModificationTestCase(unittest.TestCase):

    def test_modification(self):

        patch_form_fields()

        f = FormField()

        f.set_type(RDFS.Resource.toPython())
        f.set_value(['http://some_url.com', 'htpp://someothervalue.com'])

        self.assertEquals(f.get_value(), ['http://some_url.com', 'htpp://someothervalue.com'])

        form = Form(title='Some Form')
        form.set_type('result')

        form.add_field(var=FOAF.knows.toPython(),
                       value=['http://some_url.com', 'http://someother_vlaue.com'],
                       ftype=RDFS.Resource.toPython())

        self.assertEqual(form.get_fields().get(FOAF.knows.toPython()).get_value(),
                         ['http://some_url.com', 'http://someother_vlaue.com'])
