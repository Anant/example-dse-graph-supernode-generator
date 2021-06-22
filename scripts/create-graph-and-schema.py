from cassandra.cluster import Cluster, GraphExecutionProfile, EXEC_PROFILE_GRAPH_DEFAULT, EXEC_PROFILE_GRAPH_SYSTEM_DEFAULT, GraphOptions
import pathlib
path_to_this_file = pathlib.Path(__file__).parent.absolute()

#profile = ExecutionProfile(

graph_name = 'demo_who_likes_whom'

ep = GraphExecutionProfile(graph_options=GraphOptions(graph_name=graph_name))
cluster = Cluster(execution_profiles={EXEC_PROFILE_GRAPH_DEFAULT: ep})
session = cluster.connect()

def main():
    print("not using right now")

if __name__ == "__main__":
    main()
