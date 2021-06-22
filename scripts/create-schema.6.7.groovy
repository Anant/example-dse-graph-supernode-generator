// for DSE 6.7
// create property keys

schema.propertyKey('uuid').Uuid().single().ifNotExists().create();
schema.propertyKey('partition_key').Text().single().ifNotExists().create();
schema.propertyKey('name').Text().single().ifNotExists().create();
schema.propertyKey('info').Text().single().ifNotExists().create();

// if using composite PK, which isn't necessary for testing 6.7
//schema.vertexLabel('person').partitionKey('partition_key').clusteringKey('uuid').ifNotExists().create();
// - composite PK is harder to get working for dse graph loader, so holding off for now
schema.vertexLabel('person').partitionKey('uuid').ifNotExists().create();

// if don't want partition key for 6.7:
//schema.vertexLabel('person').ifNotExists().create();
schema.vertexLabel('person').properties('uuid', 'name','info').add();
// index, as recommended by dse graph loader dry run...and required by non-dry run!
schema.vertexLabel('person').index('byuuid').materialized().by('uuid').ifNotExists().add()

// Edge Labels
schema.edgeLabel('likes').single().ifNotExists().create();
schema.edgeLabel('likes').connection('person', 'person').add();
