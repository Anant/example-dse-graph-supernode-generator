#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# NOTE will not work with 6.7


# the dir where your data was generated. Make sure to point to the one with the right number of partitions/nodes you specified
data_dir=$1

# can specify ip optionally as first arg. If not specified will return 127.0.0.1, which is dsbulk's default anyways
# can also send list, e.g., 10.200.1.3, 10.200.1.4
ip_addr=${2:-127.0.0.1}

dsbulk load -h "$ip_addr" \
    --schema.graph demo_who_likes_whom \
    --schema.vertex person \
    -url $data_dir/vertices.csv \
    -delim '|' \
    --schema.allowMissingFields false && \

dsbulk load -h "$ip_addr" \
    -g demo_who_likes_whom \
    -e likes \
    -url $data_dir/edges.csv \
    --schema.mapping 'source_uuid=out_partition_key, target_uuid=in_partition_key, partition_key=partition_key' \
    --schema.from 'person' \
    --schema.to 'person' \
    -delim '|' \
    --schema.allowMissingFields false
