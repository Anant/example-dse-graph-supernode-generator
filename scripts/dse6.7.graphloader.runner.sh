# for 6.7 graph loader
# target dir is set in the file `./dse6.7.graphloader.run.groovy` under var `inputfiledir`, change it there to specify different data files 

# set first arg as true to do dryrun
dryrun=${1:-false}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# you can change to wherever your dsegl was downloaded to 
DSEGL_BIN=~/libs/dse-graph-loader-6.7.8/

# dry run
$DSEGL_BIN/graphloader $SCRIPT_DIR/dse6.7.graphloader.run.groovy -graph demo_who_likes_whom -address localhost -dryrun $dryrun
