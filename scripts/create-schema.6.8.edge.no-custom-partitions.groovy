// for DSE 6.8

// Edge Labels
// https://docs.datastax.com/en/dse/6.8/dse-dev/datastax_enterprise/graph/using/createEdgeLabelSchema.html
schema.edgeLabel('likes').
    ifNotExists().
    from('person').to('person').
    create()
