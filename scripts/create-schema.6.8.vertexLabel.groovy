// for DSE 6.8
// https://docs.datastax.com/en/dse/6.8/dse-dev/datastax_enterprise/graph/using/createVertLabelSchema.html

schema.vertexLabel('person').
    ifNotExists().
    // keep consistent with how we did 6.7, where it was difficult to do composite primary key, so didn't use the partition_key field after all.
    //partitionBy('partition_key', Text, 'uuid', Text).
    partitionBy('uuid', Text).
    property('name', Text).
    property('info', Text).
    create()

