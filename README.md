# Description

Creates a demo graph in DSE Graph (`demo_who_likes_whom`), generates some csv files, then loads that data. 

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

```
# python3 ./generate-csvs/generate-fake-csv.py <partition_count> <supernodes_per_partition_count> <adjacent vertices per supernode>
python3 ./generate-csvs/generate-fake-csv.py 2 2 1000000
```
This will generate 2 partitions, 4 total supernodes (each with 1,000,000 adjacent vertices), and 4,000,000 total vertices.

## 2) Create the graph and Schema 
### 2.1) for 6.7
```
./scripts/create-graph-and-schema.sh
```
- can optionally pass in ip of dse node, e.g., 
```
./scripts/create-graph-and-schema.sh 123.456.789.123
```


If it doesn't work, you can also just try manually executing the groovy scripts' contents in the gremlin-console, which is all that this shell script is doing anyway. 
```
dse gremlin-console
# then create graph and schema, copying the scripts found in ./scripts/create-graph.groovy and ./scripts/create-schema.groovy
```

### 2.2) for 6.8
Same as for 6.7, but different shell script
```
./scripts/create-graph-and-schema.6.8.sh
```




## 3) Load the data

Implementation details:
- currently does not clear out previously loaded data. 

```
# ./scripts/dse6.8.bulk-loader.runner.sh <relative-path> <ip [optional]>
./scripts/dse6.8.bulk-loader.runner.sh ./tmp/data/2-partitions.2-sn-per-p.10-v-per-sn/ 192.168.0.190
```



# Debugging
## Errors running dsbulk
### ERROR Operation LOAD_20210618-093931-387708 failed: Vertex label person does not exist.
Make sure to run scripts to create the graph and schema for dse graph first, using hte gremlin console
