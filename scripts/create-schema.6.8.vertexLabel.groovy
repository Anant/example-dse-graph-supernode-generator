// for DSE 6.8


schema.vertexLabel('person').ifNotExists().
    partitionBy('partition_key', Text).
    clusterBy('uuid', Text).
    property('name', Text).
    property('info', Text).
    create()

