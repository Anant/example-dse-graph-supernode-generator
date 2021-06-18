// for DSE 6.8


schema.vertexLabel('person').ifNotExists().
    partitionBy('partition_key', Text).
    property('uuid', Uuid).
    property('name', Text).
    property('info', Text).
    create()

