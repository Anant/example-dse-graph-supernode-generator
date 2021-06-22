// for 6.7 graph loader
inputfiledir = '/home/ryan/projects/dse-graph-supernode-benchmarking/tmp/data/2-partitions.2-sn-per-p.1000000-v-per-sn/'
// for test dataset
// inputfiledir = '/home/ryan/projects/dse-graph-supernode-benchmarking/tmp/data/1-partitions.1-sn-per-p.2-v-per-sn/'

personInput = File.csv(inputfiledir + 'intermediary-vertices.csv').delimiter('|')
likesInput = File.csv(inputfiledir + 'intermediary-vertices.edges.csv').delimiter('|')

config preparation: true, create_schema: false, load_new: true//, load_vertex_threads: 4


load(personInput).asVertices {
    label "person"
    key "uuid"
    // if using composite PK
    //key "partition_key", "uuid"
    // since NOT  using composite PK:
    ignore "partition_key"
}

// key is composite, see directions here: https://docs.datastax.com/en/dse/6.7/dse-dev/datastax_enterprise/graph/dgl/dglMapScript.html#dglCompPK
load(likesInput).asEdges {
    label "likes"
    outV "out_uuid", {
        label "person"
        // if using composite PK for vertices:
        //key out_partition_key: "partition_key", out_uuid: "uuid"
        key out_uuid: "uuid"
    }
    inV "in_uuid", {
        label "person"
        // if using composite PK for vertices:
        key in_uuid: "uuid"
    }
    ignore "edge-purpose"
}
