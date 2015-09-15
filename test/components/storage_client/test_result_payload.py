"""
Unit tests for the result payload.
"""
import unittest
from rdflib.namespace import RDF, RDFS, FOAF
from rhobot.namespace import RHO
from sleekxmpp.plugins.xep_0004.stanza.form import Form
from rhobot.components.storage import ResultCollectionPayload, ResultPayload
from rhobot.components.storage.enums import FindResults
from sleekxmpp.plugins.xep_0004 import FormField
from sleekxmpp.plugins.xep_0122 import FormValidation
from sleekxmpp.xmlstream import register_stanza_plugin


class TestResultPayload(unittest.TestCase):

    def setUp(self):
        register_stanza_plugin(FormField, FormValidation)

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

        item = result_collection_payload.results[0]

        self.assertEqual(item.about, urn)
        self.assertEqual(item.types, types)

    def test_populating(self):

        types = [str(FOAF.Person), str(RHO.Owner)]
        urn = 'urn.instance.owner'

        payload = ResultCollectionPayload()
        payload.append(ResultPayload(about=urn, types=types))

        result = payload.populate_payload()

        second_payload = ResultCollectionPayload(result)

        self.assertEqual(len(second_payload.results), len(payload.results))

        init_result = payload.results[0]
        second_result = second_payload.results[0]

        self.assertEqual(init_result.about, second_result.about)
        self.assertEqual(init_result.types, second_result.types)

        self.assertEqual(init_result.about, urn)
        self.assertEqual(init_result.types, types)

    def test_flags(self):

        types = [str(FOAF.Person), str(RHO.Owner)]
        urn = 'urn.instance.owner'
        flags = {FindResults.CREATED: False}

        payload = ResultCollectionPayload()
        payload.append(ResultPayload(about=urn, types=types, flags=flags))

        result = payload.populate_payload()

        second_payload = ResultCollectionPayload(result)

        self.assertEqual(len(second_payload.results), len(payload.results))

        init_result = payload.results[0]
        second_result = second_payload.results[0]

        self.assertEqual(init_result.about, second_result.about)
        self.assertEqual(init_result.types, second_result.types)
        self.assertEqual(FindResults.CREATED.fetch_from(init_result.flags),
                         FindResults.CREATED.fetch_from(second_result.flags))

        self.assertEqual(init_result.about, urn)
        self.assertEqual(init_result.types, types)
        self.assertEqual(FindResults.CREATED.fetch_from(init_result.flags), FindResults.CREATED.fetch_from(flags))

    def test_enum_flags(self):

        types = [str(FOAF.Person), str(RHO.Owner)]
        urn = 'urn.instance.owner'
        flags = {FindResults.CREATED: False}

        payload = ResultCollectionPayload()
        payload.append(ResultPayload(about=urn, types=types, flags=flags))

        result = payload.populate_payload()

        second_payload = ResultCollectionPayload(result)

        self.assertEqual(len(second_payload.results), len(payload.results))

        init_result = second_payload.results[0]

        self.assertEqual(init_result.about, urn)
        self.assertEqual(init_result.types, types)

        self.assertEqual(FindResults.CREATED.fetch_from(init_result.flags), False)
