# Describing RDF Data Types

RDF data types are defined through the use of XEP-0004 Data Forms.  It adds additional elements to the form fields in
order to provide details as to the values that are defined.

```xml
<rdf xmlns="urn:rho:rdf" type="publish_create">
  <x xmlns="jabber:x:data" type="form">
    <!-- Provide the unique URI for the data node -->
    <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#about" type="text-single">
      <value>http://www.example.org/instances/Instance_01</value>
    </field>
    
    <!-- Provide the details of the objects types (similar to 'a') -->
    <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" type="list-multi">
      <value>http://xmlns.com/foaf/0.1/Agent</value>
    </field>
  </x>
</rdf>
```

## Well-known Fields

There are two well known fields that are defined in the RDF definition form.  These are:
`http://www.w3.org/1999/02/22-rdf-syntax-ns#about` and `http://www.w3.org/1999/02/22-rdf-syntax-ns#type`.

### http://www.w3.org/1999/02/22-rdf-syntax-ns#about

This field will contain a single value only that provides the details of the `rdf:about` property of a specific 
instance.  

### http://www.w3.org/1999/02/22-rdf-syntax-ns#type

This field will contain a list of values that provide the data types that this instance defines.

## Additional Fields

### Defining Resource Fields

Resource fields are definitions that can be used to define the relationships between two different nodes.  This can be
used as follows:

```xml
<field var="http://xmlns.com/foaf/0.1/member" type="list-multi">
  <value>http://www.example.org/instances/member_01</value>
  <value>http://www.example.org/instances/member_02</value>
  <value>http://www.example.org/instances/member_03</value>
  <rdftype xmlns="urn:rho:rdf" type="http://www.w3.org/2000/01/rdf-schema#Resource"/>
</field>
```

In this example the `urn:rho:rdf:rdftype.type` value is defined as being rdf:Resource.

### Defining Property Fields

Property fields are definitions that can be used to define a specific property on a node.  This can be used as follows:

```xml
<field var="http://xmlns.com/foaf/0.1/name" type="list-multi">
  <value>John Smith</value>
  <rdftype xmlns="urn:rho:rdf" type="http://www.w3.org/2000/01/rdf-schema#Literal"/>
</field>
```

In this example the `urn:rho:rdf:rdftype.type` value is defined as being rdf:Literal.
