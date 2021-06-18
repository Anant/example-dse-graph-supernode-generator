#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# can specify ip optionally as first arg. If not specified will return blank
ip_addr=${1:- }

echo "running console on ip $ip_addr"
# create graph
dse gremlin-console $ip_addr -e $SCRIPT_DIR/create-graph.groovy && \

# create schema
dse gremlin-console $ip_addr -e $SCRIPT_DIR/create-schema.6.7.groovy
