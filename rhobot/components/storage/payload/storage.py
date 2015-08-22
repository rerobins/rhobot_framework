"""
Storage payload definition.  Responsible for providing basic payloads for passing node data around.
"""
from rdflib.namespace import RDF, RDFS

class StoragePayload:
    """
    Payload object that will contain the workspace for the data to be stored or looked up in the database.
    """

    def __init__(self, _container):
        self._container = _container
        self.about = None
        self._types = []
        self._properties = {}
        self._references = {}
        self._unpack_payload()

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
            value = [value]

        self._properties[key] += value

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

        self._references[key] = value

    def populate_payload(self):
        """
        Translates the contents of this object into a payload for sending across to the storage entity.
        :return: the populated form
        """
        self._container.clear()

        if self.about:
            self._container.add_field(var=str(RDF.about), value=[self.about], ftype=str(RDFS.Literal))

        if len(self._types):
            self._container.add_field(var=str(RDF.type), value=self._types, ftype=str(RDF.type))

        for key, value in self._properties.iteritems():
            self._container.add_field(var=str(key), value=value, ftype=str(RDFS.Literal))

        for key, value in self._references.iteritems():
            self._container.add_field(var=str(key), value=value, ftype=str(RDFS.Resource))

        return self._container

    def _unpack_payload(self):
        """
        Unpack the current container to class variables.
        """
        self.about = None
        self._types = []
        self._properties = {}
        self._references = {}

        for key, value in self._container.field.iteritems():
            if key == str(RDF.about):
                self.about = value.get_value()[0]
            elif value['type'] == str(RDF.type):
                self._types = value.get_value()
            elif value['type'] == str(RDFS.Literal):
                self._properties[key] = value.get_value()
            elif value['type'] == str(RDFS.Resource):
                self._references[key] = value.get_value()

    def types(self):
        return self._types

    def properties(self):
        return self._properties

    def references(self):
        return self._references
