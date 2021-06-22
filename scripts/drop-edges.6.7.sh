#!/bin/bash

DSE_DOCKER_SCRIPT_DIR=/opt/dse 
DSE_DOCKER_CONTAINER_NAME=dse-graph-supernode-benchmarking_dse_1
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# can change the command to run dse. Helpful for running with docker
use_docker=${1:-false}
# can specify ip optionally as first arg. If not specified will return blank
ip_addr=${2:- }

dse_cmd=dse
cqlsh_cmd=cqlsh

if [ "$use_docker" = true ] ; then
    # copy the groovy scripts over
    docker cp $SCRIPT_DIR/drop-edges.6.7.groovy $DSE_DOCKER_CONTAINER_NAME:$DSE_DOCKER_SCRIPT_DIR
    dse_cmd="docker exec -it $DSE_DOCKER_CONTAINER_NAME dse"
    cqlsh_cmd="docker exec -it $DSE_DOCKER_CONTAINER_NAME cqlsh"

    # point to dir in dse docker container
    SCRIPT_DIR=$DSE_DOCKER_SCRIPT_DIR
fi

echo "running console on ip ${ip_addr}"
# drop all edges
# 40 should be about enough (100,000 dropped each time)
# 50 should definitely do the trick
# change your gc_grace_seconds to really get this moving. It's safe, assuming this is a single node cluster, which is how it's setup in docker
$cqlsh_cmd -e " ALTER TABLE demo_who_likes_whom.person_e WITH gc_grace_seconds = 1;"

ran_times=0
count=5

# every 10 times, do a compact
for i in $(seq $count); do
		for i in $(seq 10); do
				$dse_cmd gremlin-console $ip_addr -e $SCRIPT_DIR/drop-edges.6.7.groovy 
        ran_times=$((ran_times+1))
				echo "dropping 100,000 edges...($ran_times so far)"
		done
    echo "(compact once to remove tombstones)"
		$dse_cmd nodetool compact
done
