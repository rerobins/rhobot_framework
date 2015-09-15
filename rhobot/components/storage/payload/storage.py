"""
Storage payload definition.  Responsible for providing basic payloads for passing node data around.
"""
from rdflib.namespace import RDF
from sleekxmpp.plugins.xep_0004 import Form
from sleekxmpp.plugins.xep_0122 import FormValidation
from rhobot.components.storage.enums import Flag

class StoragePayload:
    """
    Payload object that will contain the workspace for the data to be stored or looked up in the database.
    """

    def __init__(self, _container=None):

        self.about = None
        self._types = []
        self._properties = {}
        self._references = {}
        self._flags = {}

        if _container:
            self._unpack_payload(_container)

    def add_type(self, *args):
        """
        Add a list of types to the container.
        :param args:
        :return:
        """
        for arg in args:
            self._types.append(str(arg))

    def add_property(self, key, value):
        """
        Add a property to the list of values for storage.
        :param key:
        :param value: should be a list, otherwise will be converted to a list.
        :return:
        """
        if key not in self._properties:
            self._properties[key] = []

        if not isinstance(value, list):
            value = [str(value)]

        current_values = self._properties[key]
        for val in value:
            current_values.append(str(val))

    def add_reference(self, key, value):
        """
        Add a reference to the list of values for storage.
        :param key:
        :param value: should be a list, otherwise will be converted to a list.
        :return:
        """
        if key not in self._references:
            self._references[key] = []

        if not isinstance(value, list):
            value = [value]

        current_values = self._references[key]
        for val in value:
            current_values.append(str(val))

    def add_flag(self, enumeration, value=None):
        """
        Add a flag to the payload.
        :param enumeration: enumeration that should return a dict as a value.
        :param value:
        :return:
        """
        true_value = value
        if not value:
            true_value = enumeration.value['value']

        self._flags[enumeration] = true_value

    def populate_payload(self, _container=None):
        """
        Translates the contents of this object into a payload for sending across to the storage entity.
        :return: the populated form
        """

        if _container:
            container = _container
        else:
            container = Form()

        if self.about:
            container.add_field(var=str(RDF.about), value=str(self.about), ftype='text-single')

        if len(self._types):
            container.add_field(var=str(RDF.type), value=self._types, ftype='list-multi')

        for key, value in self._properties.iteritems():
            property_field = container.add_field(var=str(key), value=value, ftype='list-multi')
            type_stanza = FormValidation()
            type_stanza['datatype'] = 'xs:string'
            property_field.append(type_stanza)

        for key, value in self._references.iteritems():
            reference_field = container.add_field(var=str(key), value=value, ftype='list-multi')
            type_stanza = FormValidation()
            type_stanza['datatype'] = 'xs:anyURI'
            reference_field.append(type_stanza)

        for key, value in self._flags.iteritems():
            container.add_field(var=key.var, value=value, ftype=key.field_type)

        return container

    def _unpack_payload(self, container):
        """
        Unpack the current container to class variables.
        """
        self.about = None
        self._types = []
        self._properties = {}
        self._references = {}

        for key, value in container.field.iteritems():
            rdf_type = value['validate']['datatype']
            field_type = value['type']

            if key == str(RDF.about):
                self.about = value.get_value()
            elif key == str(RDF.type):
                self._types = value.get_value()
            elif rdf_type == 'xs:string':
                self._properties[key] = value.get_value()
            elif rdf_type == 'xs:anyURI':
                self._references[key] = value.get_value()
            else:
                key = Flag(*(key, field_type, None))
                self._flags[key] = value.get_value()

    @property
    def types(self):
        return self._types

    @property
    def properties(self):
        return self._properties

    @property
    def references(self):
        return self._references

    @property
    def flags(self):
        return self._flags
