// for DSE 6.8

// Edge Labels
// https://docs.datastax.com/en/dse/6.8/dse-dev/datastax_enterprise/graph/using/createEdgeLabelSchema.html
schema.edgeLabel('likes').
    ifNotExists().
    from('person').to('person').
    // this is if partitioning by the source person's (ie, the non-supernode's) uuid
    // partitionBy(OUT, 'uuid', 'source_uuid')
    partitionBy('custom_partition_key', Text).
    create()
