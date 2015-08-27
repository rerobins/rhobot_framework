"""
Unit tests for the result payload.
"""
import unittest
from rdflib.namespace import RDF, RDFS, FOAF
from rhobot.namespace import RHO
from sleekxmpp.plugins.xep_0004.stanza.form import Form
from rhobot.components.storage import ResultCollectionPayload, ResultPayload
from rhobot.stanza_modification import patch_form_fields; patch_form_fields()


class TestResultPayload(unittest.TestCase):
    def test_parsing(self):
        form = Form()

        types = [str(FOAF.Person), str(RHO.Owner)]
        urn = 'urn.instance.owner'

        form.add_reported(var=str(RDF.about), ftype=str(RDFS.Literal))
        form.add_reported(var=str(RDF.type), ftype=str(RDF.type))

        form.add_item({str(RDF.about): urn,
                       str(RDF.type): types})

        result_collection_payload = ResultCollectionPayload(form)

        self.assertEqual(len(form.get_items()), len(result_collection_payload._results))

    def test_populating(self):

        types = [str(FOAF.Person), str(RHO.Owner)]
        urn = 'urn.instance.owner'

        payload = ResultCollectionPayload()
        payload.append(ResultPayload(about=urn, types=types))

        result = payload.populate_payload()

        second_payload = ResultCollectionPayload(result)

        self.assertEqual(len(second_payload.results()), len(payload.results()))

        init_result = payload.results()[0]
        second_result = second_payload.results()[0]

        self.assertEqual(init_result.about, second_result.about)
        self.assertEqual(init_result.types(), second_result.types())

        self.assertEqual(init_result.about, urn)
        self.assertEqual(init_result.types(), types)

if __name__ == '__main__':
    unittest.main()
