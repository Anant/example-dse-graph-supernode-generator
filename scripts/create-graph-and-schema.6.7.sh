#!/bin/bash

DSE_DOCKER_SCRIPT_DIR=/opt/dse 
DSE_DOCKER_CONTAINER_NAME=dse-graph-supernode-benchmarking_dse_1
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# can change the command to run dse. Helpful for running with docker
use_docker=${1:-false}
# can specify ip optionally as first arg. If not specified will return blank
ip_addr=${2:- }

dse_cmd=dse

if [ "$use_docker" = true ] ; then
    # copy the groovy scripts over
    docker cp $SCRIPT_DIR/create-graph.groovy $DSE_DOCKER_CONTAINER_NAME:$DSE_DOCKER_SCRIPT_DIR
    docker cp $SCRIPT_DIR/create-schema.6.7.groovy $DSE_DOCKER_CONTAINER_NAME:$DSE_DOCKER_SCRIPT_DIR
    docker cp $SCRIPT_DIR/setup-remote.groovy $DSE_DOCKER_CONTAINER_NAME:$DSE_DOCKER_SCRIPT_DIR
    dse_cmd="docker exec -it $DSE_DOCKER_CONTAINER_NAME dse"

    # point to dir in dse docker container
    SCRIPT_DIR=$DSE_DOCKER_SCRIPT_DIR
fi

echo "running console on ip ${ip_addr}"
# create graph
$dse_cmd gremlin-console $ip_addr -e $SCRIPT_DIR/create-graph.groovy && \

# create schema
$dse_cmd gremlin-console $ip_addr -e $SCRIPT_DIR/setup-remote.groovy -e $SCRIPT_DIR/create-schema.6.7.groovy
