import csv
import math
import argparse
from faker import Faker
import datetime
import uuid
import os
import shutil
from pathlib import Path 

current_file_abs_path = Path(__file__).parent.absolute()
fake = Faker('en_US')


class Generator():
    """
    Implementation details:
    - currently only a single hop depth. Perhaps later can add other details and programmatic ways to add hops
    - currently a single v label, so edge goes back to same v label
    - does not allow specifying by MB yet
    - deletes old data from previous run when script is ran again, if same counts are given

    Warnings: 
    - due to use of range, make sure to use python3 for performance reasons

    """
    supernodes = []

    # NOTE order matters, due to how are writing to CSV
    vertices_headers = ["uuid", "partition_key", "name", "info"]
    # partition_key will only be used for 6.8, for 6.7 can't partition on edges, so not used, it's just ignored
    edges_headers = ["out_uuid", "in_uuid", "out_partition_key", "in_partition_key","custom_partition_key"]

    def __init__(self, partition_count, supernodes_per_partition_count, adj_v_per_supernode):
        self.partition_count = partition_count
        self.supernodes_per_partition_count = supernodes_per_partition_count
        self.adj_v_per_supernode = adj_v_per_supernode


        # calculate some other values
        self.supernode_count = self.supernodes_per_partition_count * self.partition_count
        self.total_v_count = self.supernodes_per_partition_count * self.adj_v_per_supernode * self.partition_count
        # for now, the same. One e per v, except the supernodes themselves don't have an edge
        self.total_e_count = self.total_v_count - self.supernodes_per_partition_count


        self.tmp_data_path = os.path.join(current_file_abs_path, f"../tmp/data/{self.partition_count}-partitions.{self.supernodes_per_partition_count}-sn-per-p.{self.adj_v_per_supernode}-v-per-sn")
        self.vertices_csv_filename = os.path.join(self.tmp_data_path, f"vertices.csv")
        self.edges_csv_filename = os.path.join(self.tmp_data_path, f"edges.csv")
        self.supernodes_uuids_txt_filename = os.path.join(self.tmp_data_path, f"supernodes_uuids.txt")

    def generate_vertex_info(self, partition_key):
        """
        generates the data to be written to CSV row for a single row
        - for now incrementing integer works fine
        """
        
        return {
            "uuid": uuid.uuid4(),
            "partition_key": partition_key,
            "name": fake.name(),
            "info": fake.sentence()
            }


    def generate_other_vertices_with_edges(self):
        """
        - supernodes are already generated at thispoint. 
        - Now generate adjacent vertices and their edges
        """

        # keeping a counter going
        vertices_finished = 0

        with open(self.vertices_csv_filename, 'a') as vFile, open(self.edges_csv_filename, 'a') as eFile:
            vWriter = csv.writer(vFile, delimiter = '|')
            eWriter = csv.writer(eFile, delimiter = '|')

            for supernode in self.supernodes:
                # TODO might do this differently so we don't have to have as much in memory. But I think this is faster for file IO since it has 
                for i in range(self.adj_v_per_supernode):

                    ##############################
                    # make vertex
                    # - uses same partition key as its supernode, for now
                    connected_v = self.generate_vertex_info(supernode["partition_key"])

                    # write to csv as vertex
                    # - create tuple of data
                    v_data_to_write = (connected_v[header] for header in self.vertices_headers)
                    # - write to row
                    vWriter.writerow(v_data_to_write)

                    ##############################
                    # make edge connecting it to supernode
                    # source then target
                    # e.g., Fan123 likes JustinBieber (the supernode)
                    # for now, assuming only 6.7, so no edge partition key setting is allowed. But setting the value so can use same csv file for 6.8. For now, setting to just supernode's partition_key. Then we can run some etl to move edges to different partition for different tests
                    # if we do use custom_partition_key, just add the non-supernode's partition key
                    custom_partition_key = connected_v["partition_key"]
                    e_data_to_write = (connected_v["uuid"], supernode["uuid"], connected_v["partition_key"], supernode["partition_key"], custom_partition_key)
                    eWriter.writerow(e_data_to_write)

                vertices_finished = vertices_finished + self.adj_v_per_supernode
                print("finished vertices:", vertices_finished)


    def generate_supernode_vertices(self):
        """
        - note that the output will not be actual supernode yet, just the vertices for the super nodes
        """

        with open(self.vertices_csv_filename, 'a') as v_csvFile, open(self.supernodes_uuids_txt_filename, 'w') as sn_txtFile:
            v_writer = csv.writer(v_csvFile, delimiter = '|')

            for partition_i in range(self.partition_count):
                for i in range(self.supernodes_per_partition_count):
                    supernode_v = self.generate_vertex_info(partition_i)
                    # put into memory. Should be small number, so safe to put in memory
                    self.supernodes.append(supernode_v)

                    # write to csv as vertex
                    # - create tuple of data
                    data_to_write = (supernode_v[header] for header in self.vertices_headers)
                    # - write to row
                    v_writer.writerow(data_to_write)

                    # write uuid down for this sn
                    sn_txtFile.write(str(supernode_v["uuid"]) + "\n")

    

    def initialize_csv_files(self):
        """
        - write headers for both csvs
        """

        # remove existing data and make tmp dir
        if not os.path.exists(self.tmp_data_path):
            Path(self.tmp_data_path).mkdir(parents=True, exist_ok=True)

        # for vertices
        # note that w mode will clear existing lines in file if exists
        with open(self.vertices_csv_filename, 'w') as csvFile:
            v_writer = csv.writer(csvFile, delimiter = '|')
            v_writer.writerow(self.vertices_headers)

        # for edges
        # note that w mode will clear existing lines in file if exists
        with open(self.edges_csv_filename, 'w') as csvFile:
            e_writer = csv.writer(csvFile, delimiter = '|')
            e_writer.writerow(self.edges_headers)

    def convert_size(self, size_bytes):
        """
        - credit: https://stackoverflow.com/a/14822210/6952495
        """

        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    def print_file_metrics(self):
        
        vertices_file_size = os.path.getsize(self.vertices_csv_filename)
        edges_file_size = os.path.getsize(self.edges_csv_filename)
        print("\n====================\nMetrics:")
        print("====================")
        print("partition count:", self.partition_count)
        print("supernodes per partition count:", self.supernodes_per_partition_count)
        print("adjacent vertices per supernode count:", self.adj_v_per_supernode)
        print("total vertices count:", self.total_v_count)
        print("total edges count:", self.total_e_count)
        print("== vertices file size:", self.convert_size(vertices_file_size))
        print("== edges file size:", self.convert_size(vertices_file_size))

    def main(self):
        self.initialize_csv_files()
        self.generate_supernode_vertices()
        self.generate_other_vertices_with_edges()
        print("done.\n")
        self.print_file_metrics()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Collecting config varibales from environments.yaml and Start receiving stats',
            usage=' <partition_count> <supernodes_per_partition_count> <adjacent vertices per supernode>')

    parser.add_argument('partition_count', type=str, help='defaults to 2', default=2)
    parser.add_argument('supernodes_per_partition_count', type=str, help='defaults to 2', default=2)
    parser.add_argument('adj_v_per_supernode', type=str, help='Adjacent versus per supernode. defaults to 10', default=10)

    args = parser.parse_args()

    # number of supernodes
    partition_count = int(args.partition_count)
    supernodes_per_partition_count = int(args.supernodes_per_partition_count)
    # records will be evenly distributed between supernodes
    adj_v_per_supernode = int(args.adj_v_per_supernode)

    generator = Generator(partition_count, supernodes_per_partition_count, adj_v_per_supernode)
    generator.main()

