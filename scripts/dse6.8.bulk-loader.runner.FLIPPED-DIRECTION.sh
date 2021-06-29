#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# NOTE will not work with 6.7

# set first arg as true to do dryrun
dryrun=${1:-false}


# the dir where your data was generated. Make sure to point to the one with the right number of partitions/nodes you specified
data_dir=$2

# can specify ip optionally as first arg. If not specified will return 127.0.0.1, which is dsbulk's default anyways
# can also send list, e.g., 10.200.1.3, 10.200.1.4
ip_addr=${3:-127.0.0.1}

dsbulk load -h "$ip_addr" \
    -dryRun $dryrun \
    --schema.graph demo_who_likes_whom \
    --schema.vertex person \
    -url $data_dir/vertices.csv \
    -delim '|' \
    --schema.allowMissingFields false && \

    # basically, everything is the same in this entire script as the non-flipped version, but this one makes the out_uuid the in instead
dsbulk load -h "$ip_addr" \
    -dryRun $dryrun \
    -g demo_who_likes_whom \
    -e likes \
    -url $data_dir/edges.csv \
    --schema.mapping 'out_uuid=in_uuid, in_uuid=out_uuid' \
    --schema.from 'person' \
    --schema.to 'person' \
    -delim '|' \
    --schema.allowMissingFields false
