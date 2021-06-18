// for DSE 6.7

schema.config().option('graph.schema_mode').set('Development')
schema.config().option('graph.allow_scan').set('true')

:remote config alias g demo_who_likes_whom.g
// create property keys
// TODO / NOTE not yet tested

schema.propertyKey('uuid').Uuid().single().ifNotExists().create()
schema.propertyKey('partition_key').Text().ifNotExists().single().create()
schema.propertyKey('name').Text().single().ifNotExists().create()
schema.propertyKey('info').Text().single().ifNotExists().create()

schema.vertexLabel('person').ifNotExists().partitionKey('partition_key').create()
schema.vertexLabel('person').properties('uuid', 'name','info').add()

// Edge Labels
schema.edgeLabel('likes').ifNotExists().connection('person','person').create()
