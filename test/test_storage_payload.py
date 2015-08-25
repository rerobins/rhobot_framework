import unittest
from rdflib.namespace import RDF, RDFS, FOAF
from rhobot.namespace import RHO
from sleekxmpp.plugins.xep_0004.stanza.form import Form
from rhobot.components.storage import StoragePayload
from rhobot.components.storage.enums import FindFlags
from rhobot.stanza_modification import patch_form_fields; patch_form_fields()


class TestStoragePayload(unittest.TestCase):

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

        self.assertEqual(content.get_fields()[str(RDF.about)]['value'], [about])
        self.assertEqual(content.get_fields()[str(RDFS.seeAlso)]['value'], [see_also])
        self.assertEqual(content.get_fields()[str(FOAF.mbox)]['value'], [mbox])
        self.assertEqual(content.get_fields()[FindFlags.CREATE_IF_MISSING.value['var']]['value'], create_if_missing)

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
        self.assertEqual(second_payload.properties()[str(RDFS.seeAlso)], [see_also])
        self.assertEqual(second_payload.references()[str(FOAF.mbox)], [mbox])
        self.assertEqual(second_payload.flags()[FindFlags.CREATE_IF_MISSING.value['var']], create_if_missing)
