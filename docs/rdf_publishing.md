# RDF Publishing and Searching

RDF publishing and searching occurs inside the discovery channel.  Since XMPP MUC doesn't support the broadcasting of 
IQ stanzas to all of the members, the broadcasting must be done through message stanzas instead.

## Publish Modifications to Data Models

It is required that each bot that creates or modifies a data model, those modifications SHOULD be published to the 
discovery channel for other bots in the system to process their contents.

### Create

This message type is fired off ONLY WHEN new data is created.  It should contain the
`http://www.w3.org/1999/02/22-rdf-syntax-ns#about` and `http://www.w3.org/1999/02/22-rdf-syntax-ns#type` fields.  The
about field should be populated with the value of the urn to the instance.  The type field should contain all of the
types that define this subject's defined types.

```xml
<message to="channel@conference.example.org" type="groupchat">
  <body>Some Body</body>
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
</message>
```

In this example the `urn:rho:rdf:rdf.type` is set to `publish_create`.

### Update

This message type is fired off ONLY WHEN current data is modified.
  
```xml
<message to="channel@conference.example.org" type="groupchat">
  <body>Some Body</body>
  <rdf xmlns="urn:rho:rdf" type="publish_update">
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
</message>
```

In this example the `urn:rho:rdf:rdf.type` is set to `publish_update`.
 
## Search Request

Searching is also built upon the `message` stanzas, but takes advantage of `thread` identifiers inside the message.

### Requesting Search Payload

The following message is fired off to request all knowing members of the discovery channel to search for data members 
that provide the required functionality.

```xml
<message to="channel@conference.example.org" type="groupchat">
  <body>Some Body</body>

  <rdf xmlns="urn:rho:rdf" type="request">
    <x xmlns="jabber:x:data" type="form">
      <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" type="list-multi">
        <value>http://xmlns.com/foaf/0.1/Agent</value>
      </field>
    </x>
  </rdf>
  
  <thread>
    e0ffe42b28561960c6b12b944a092794b9683a38
  </thread>
  
</message>
```

In this example the requester is requesting that any of the members in the channel provide responses about data models
that are defined by the FOAF:Agent data definition. 

#### Important content

* thread value should be used by all responders in order to correlate results with requests.
* `urn:rho:rdf:rdf.type` is set to request.

## Search Responses

Responding to search requests are implemented as `message` stanzas.

```xml
<message to="channel@conference.example.org" type="groupchat">
  <body>Some Body</body>

  <rdf xmlns="urn:rho:rdf" type="response">
    <x xmlns="jabber:x:data" type="form">
      <reported>
        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#about" type="text-single" />
        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" type="list-multi" />
      </reported>
      <item>
        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#about">
          <value>http://www.example.org/instances/Agent01
        </field>
        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type">
          <value>http://xmlns.com/foaf/0.1/Agent</value>
        </field>
      </item>
      <item>
        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#about">
          <value>http://www.example.org/instances/Agent02
        </field>
        <field var="http://www.w3.org/1999/02/22-rdf-syntax-ns#type">
          <value>http://xmlns.com/foaf/0.1/Agent</value>
        </field>
      </item>
    </x>
    
    <source name="Bot Name" command="xmpp:channel@conference.example.org/nick?command;node=command_node" />
  </rdf>
  
  <thread>
    e0ffe42b28561960c6b12b944a092794b9683a38
  </thread>
  
</message>
```

This example shows a response to the search request.  It returns two items that match the search request details.

