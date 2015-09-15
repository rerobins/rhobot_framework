import unittest
from rdflib.namespace import RDF, RDFS, FOAF
from sleekxmpp.plugins.xep_0004.stanza.form import Form
from rhobot.components.storage import StoragePayload
from rhobot.components.storage.enums import FindFlags
from rhobot.stanza_modification import patch_form_fields; patch_form_fields()
from sleekxmpp.plugins.xep_0122 import FormValidation
from sleekxmpp.plugins.xep_0004 import FormField
from sleekxmpp.xmlstream import register_stanza_plugin


class TestStoragePayload(unittest.TestCase):

    def setUp(self):
        register_stanza_plugin(FormField, FormValidation)

    def test_populate(self):

        form = Form()

        payload = StoragePayload(form)

        about = 'urn:rho:identified_by:asdf'
        see_also = 'urn:rho.value'
        mbox = 'mailto:email@example.com'
        create_if_missing = True

        payload.about = about

        payload.add_type(FOAF.Person)
        payload.add_property(RDFS.seeAlso, see_also)
        payload.add_reference(FOAF.mbox, mbox)
        payload.add_flag(FindFlags.CREATE_IF_MISSING, create_if_missing)

        content = payload.populate_payload()

        self.assertEqual(content.get_fields()[str(RDF.about)].get_value(), about)
        self.assertEqual(content.get_fields()[str(RDFS.seeAlso)].get_value(), [see_also])
        self.assertEqual(content.get_fields()[str(FOAF.mbox)].get_value(), [mbox])
        self.assertEqual(content.get_fields()[FindFlags.CREATE_IF_MISSING.var].get_value(), create_if_missing)

    def test_unpack(self):

        form = Form()

        payload = StoragePayload(form)

        about = 'urn:rho:identified_by:asdf'
        see_also = 'urn:rho.value'
        mbox = 'mailto:email@example.com'
        create_if_missing = True

        payload.about = about

        payload.add_type(FOAF.Person)
        payload.add_property(RDFS.seeAlso, see_also)
        payload.add_reference(FOAF.mbox, mbox)
        payload.add_flag(FindFlags.CREATE_IF_MISSING, create_if_missing)

        content = payload.populate_payload()

        second_payload = StoragePayload(content)

        self.assertEqual(second_payload.about, about)
        self.assertIn(str(FOAF.Person), second_payload.types)
        self.assertEqual(second_payload.properties[str(RDFS.seeAlso)], [see_also])
        self.assertEqual(second_payload.references[str(FOAF.mbox)], [mbox])

        self.assertEqual(FindFlags.CREATE_IF_MISSING.fetch_from(second_payload.flags), create_if_missing)

    def test_pack_unpacked_payload(self):

        form = Form()

        payload = StoragePayload(form)

        about = 'urn:rho:identified_by:asdf'
        see_also = 'urn:rho.value'
        mbox = 'mailto:email@example.com'
        create_if_missing = True

        payload.about = about

        payload.add_type(FOAF.Person)
        payload.add_property(RDFS.seeAlso, see_also)
        payload.add_reference(FOAF.mbox, mbox)
        payload.add_flag(FindFlags.CREATE_IF_MISSING, create_if_missing)

        content = payload.populate_payload()

        second_payload = StoragePayload(content)

        second_content = second_payload.populate_payload()

        self.assertIsNotNone(second_content)

        self.assertEqual(second_content.get_fields()[str(RDF.about)].get_value(), about)
        self.assertEqual(second_content.get_fields()[str(RDFS.seeAlso)].get_value(), [see_also])
        self.assertEqual(second_content.get_fields()[str(FOAF.mbox)].get_value(), [mbox])
        self.assertEqual(second_content.get_fields()[FindFlags.CREATE_IF_MISSING.var].get_value(), create_if_missing)
