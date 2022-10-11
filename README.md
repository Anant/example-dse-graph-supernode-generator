# Description

Creates a demo graph in DSE Graph (`demo_who_likes_whom`), generates some csv files, then loads that data. 

See also three part blog series: https://anant.us/blog/partitioning-in-dse-graph/

## Use cases
- Benchmarking
- Performance testing
- Data model experimentation

## Implementation Details
- Not yet including indices in the testing
- Single hop writes/reads only, not worrying about depth yet

# Instructions

## 0) Install
### 0.1) Python reqs
```
python3 -m venv ./venv 
source venv/bin/activate
pip3 install -r requirements
```

### 0.2) Install GraphLoader (for 6.7)
      ```
      curl -OL https://downloads.datastax.com/enterprise/dse-graph-loader-6.7.tar.gz
      tar -xzvf dse-graph-loader-6.7.tar.gz
      ```
TODO

### 0.3) DSbulk (for 6.8)
Following: https://docs.datastax.com/en/dse/6.8/dse-admin/datastax_enterprise/graph/using/graphInstallDSbulk.html

- Download and unpackage

      ```
      curl -OL https://downloads.datastax.com/dsbulk/dsbulk-1.8.0.tar.gz
      tar -xzvf dsbulk-1.8.0.tar.gz
      ```
- Set to PATH
    * this is required if you want to use our shell script to load
        ```
        echo 'export PATH=/home/ryan/libs/dsbulk-1.8.0/bin:$PATH' >> ~/.bashrc 
        source ~/.bashrc
        dsbulk --version

        ```

- You might also need to perform some of the steps defined here: https://docs.datastax.com/en/dsbulk/doc/dsbulk/install/dsbulkInstall.html#Post-installrequirementsandrecommendations

## 1) Generate csvs

**NOTE** currently <partition_count> <supernodes_per_partition_count> are really misnomers. Partition key is just the uuid of the supernode, so e.g., if you do 2 and 2 (as below) there should be four supernodes. Later can go back and readjust so that it actually creates 2 partitions and 2 supernodes per, but it wasn't needed for our use case after all so abandoned that and haven't fixed yet TODO


```
# python3 ./generate-csvs/generate-fake-csv.py <partition_count> <supernodes_per_partition_count> <adjacent vertices per supernode>
python3 ./generate-csvs/generate-fake-csv.py 2 2 1000000
```
This will generate 2 partitions, 4 total supernodes (each with 1,000,000 adjacent vertices), and 4,000,000 total vertices.

## 2) Create the graph and Schema 
### 2.1) for 6.7
- Start docker container for 6.7 (if using our docker setup)
    ```
    docker-compose -f docker-compose.6.7.yml up -d
    ```
- Then run it
```
./scripts/create-graph-and-schema.6.7.sh
```

- can optionally pass in ip of dse node, and specify if executing against provided docker-compose file e.g., if not running with docker, and if specifying ip:
```
./scripts/create-graph-and-schema.6.7.sh false 123.456.789.123
```
or if you are using docker:
```
./scripts/create-graph-and-schema.6.7.sh true
```


If it doesn't work, you can also just try manually executing the groovy scripts' contents in the gremlin-console, which is all that this shell script is doing anyway. 
```
dse gremlin-console
# then create graph and schema, copying the scripts found in ./scripts/create-graph.groovy and ./scripts/create-schema.groovy
```

### 2.2) for 6.8
Same as for 6.7, but different shell script and docker compose file. Note that this will not work on the same computer with 6.7 running, so either do all of 6.7 tests then 6.8 or whatever you want to do, but make sure to stop that container first. 

- Start docker container for 6.8 (if using our docker setup)
    ```
    docker-compose -f docker-compose.6.8.yml up -d
    ```
- Then run it:
We're going to start with the schema for the control first, ie, no custom partitions for edges. For 6.7 the control and the test data could share the same schema, but the same is not true for 6.8 where the edges will have a different partitionKey set in the test. 

```
./scripts/create-graph-and-schema.6.8.no-custom-partitions.sh
```




## 3) Load data for the control 
### 3.1) Load data for 6.7

- Dry run

    ```
    ./scripts/dse6.7.graphloader.runner.sh true
    ```

- When ready, execute
    ```
    ./scripts/dse6.7.graphloader.runner.sh
    ```

    Note that this can take a long time, but you can take the supernode ids from the generated file (e.g., `./tmp/data/2-partitions.2-sn-per-p.1000000-v-per-sn/supernodes_uuids.txt`) and start querying, since supernodes will probably be written first, being at the top of the `vertices.csv` file
      * E.g., if one has uuid of `53eb72bd-7a7a-4ff3-b0de-451eab371b05`, can do:
          ```
          g.V().hasLabel("person").has("uuid", "53eb72bd-7a7a-4ff3-b0de-451eab371b05")
          ```

### 3.2) Load Data for 6.8 control (with NO partition keys for edges)
    ./scripts/dse6.8.bulk-loader.runner.sh <dryRun> <data-dir-path> <c*-ip>

    E.g.: for dry run
    ```
    ./scripts/dse6.8.bulk-loader.runner.sh true ./tmp/data/2-partitions.2-sn-per-p.1000000-v-per-sn 127.0.0.1
    ```

    E.g.: for actual execute
    ```
    ./scripts/dse6.8.bulk-loader.runner.sh false ./tmp/data/2-partitions.2-sn-per-p.1000000-v-per-sn 127.0.0.1
    ```


# 4) Generate Intermediary vertices for 6.7

Note: If your 6.7 db already has data, you will want to either clear everything out by wiping clean the db of at least all the edges, or use our helper script. 

Wiping the db clean (or building a new container from the docker image for that matter) is safe and simple, but of course you will need to ingest all of the vertices all over again. The helper script was made to just clear out the edges:

```
./scripts/drop-edges.6.7.sh
```

## 4.1) Generate CSV
This is for 6.7 only, to see how this solution works
```
python3 generate-csvs/generate-fake-csv.generate-intermediary-vertices.py <path to data dir> <max incoming edges for intermediary vertex>
```
e.g., 
```
python3 generate-csvs/generate-fake-csv.generate-intermediary-vertices.py ./tmp/data/2-partitions.2-sn-per-p.10-v-per-sn/ 3
```

## 4.2) Load intermediary vertices into db

- If there's edges already, make sure to drop all existing edges. Vertices are fine
    ```
    # NOTE will change your gc_grace_seconds for person_p, but that should be fine since this is a single node cluster
    ./scripts/drop-edges.6.7.sh true
    ```

## 5) Load data For 6.8, with partition keys for edges

Implementation details:
- currently does not clear out previously loaded data. 
    * You will want a totally empty db before starting, at the very least for our test keyspace and test table, so that you can confirm the size of partitions after all data is ingested. However our script does not do that for you. 
- The original csv created should have working partition keys for the edges on that csv already so no new csv should need to be created.

- If there's edges already, make sure to drop all existing edges. Vertices are fine
    ```
    # NOTE will change your gc_grace_seconds for person_p, but that should be fine since this is a single node cluster
    ./scripts/drop-edges.6.7.sh true
    ```

```
# ./scripts/dse6.8.bulk-loader.runner.sh <relative-path> <ip [optional]>
./scripts/dse6.8.bulk-loader.runner.sh ./tmp/data/2-partitions.2-sn-per-p.10-v-per-sn/ 192.168.0.190
```





# Development
## Helpful tricks/Scripts
### Run gremlin queries in gremlin console
    ```
    docker exec -it dse-graph-supernode-benchmarking_dse_1 dse gremlin-console
    :remote config alias g demo_who_likes_whom.g
    ```
Then you should be good to go, e.g.,
```
g.V().limit(10)
```

Of course, for the 6.8 image, use the right name for that instead (`dse-graph-supernode-benchmarking_dse_6_8`)

### Drop graph and create schema again
- in Gremlin console: 

    ```
    docker exec -it dse-graph-supernode-benchmarking_dse_1 dse gremlin-console
    system.graph('demo_who_likes_whom').drop()
    ```
- Then in host Bash, build again:
    ```
    # for 6.7
    ./scripts/create-graph-and-schema.6.7.sh true
    ```

Of course, for the 6.8 image, use the right name for that instead (`dse-graph-supernode-benchmarking_dse_6_8`)

# Debugging
## Errors running DSE graph loader
- Try making a smaller sample set, then changing the target csv file when executing
    ```
    python3 ./generate-csvs/generate-fake-csv.py 1 1 2
    vim ./scripts/dse6.7.graphloader.run.groovy
    # and then change the target csv to inputfiledir = '/home/ryan/projects/dse-graph-supernode-benchmarking/tmp/data/1-partitions.1-sn-per-p.2-v-per-sn/'
    ```
## Errors running dsbulk
### ERROR Operation LOAD_20210618-093931-387708 failed: Vertex label person does not exist.
Make sure to run scripts to create the graph and schema for dse graph first, using hte gremlin console
