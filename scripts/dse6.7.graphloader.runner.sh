# for 6.7 graph loader
inputfiledir = '/home/ryan/projects/dse-graph-supernode-benchmarking/tmp/data'
personInput = File.csv(inputfiledir + 'vertices.csv').delimiter('|')
likesInput = File.csv(inputfiledir + 'edges.csv').delimiter('|')

load(personInput).asVertices {
    label "person"
    key "uuid"
}

load(likesInput).asEdges {
    label "likes"
    outV "source_uuid", {
        label "person"
        key "uuid"
    }
    inV "target_uuid", {
        label "person"
        key "uuid"
    }
}


# dry run
graphloader authorBookMappingCSV.groovy -graph testCSV -address localhost -dryrun true
