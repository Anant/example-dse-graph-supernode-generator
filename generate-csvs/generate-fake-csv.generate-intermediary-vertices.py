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


class IntermediaryNodeGenerator():
    """
    """
    supernode_uuids = []

    # list of intermediary vertices
    intermediary_vertices = []

    # NOTE order matters, due to how are writing to CSV
    vertices_headers = ["uuid", "partition_key", "name", "info"]
    # partition_key will only be used for 6.8, for 6.7 can't partition on edges, so not used, it's just ignored
    edges_headers = ["out_uuid", "in_uuid", "edge-purpose"]

    # for when running generate_intermediary_edges
    current_iv = None
    remaining_intermediary_vertices = None
    current_supernode_uuid = None
    current_count_for_iv = 0

    def __init__(self, data_dir_path, edges_per_intermediary_v):
        self.data_dir_path = os.path.dirname(data_dir_path)

        self.edges_per_intermediary_v = edges_per_intermediary_v
        print(f"directory path is: {self.data_dir_path}")
        self.data_dir_name = self.data_dir_path.split("/")[-1]

        # e.g., for a file named "2-partitions.2-sn-per-p.1000000-v-per-sn":
        print(f"directory name is: {self.data_dir_name}")
        data_file_info = self.data_dir_name.split(".")
        # - this would be 2
        self.partition_count = int(data_file_info[0].split("-")[0])

        # - this would be 2
        self.supernodes_per_partition_count = int(data_file_info[1].split("-")[0])
        # - this would be 1000000
        self.adj_v_per_supernode = int(data_file_info[2].split("-")[0])


        ###################
        # calculate some other values
        # - how many intermediary vertices we'll need per supernode
        self.intermediary_v_per_sn_count = int(math.ceil(self.adj_v_per_supernode / self.edges_per_intermediary_v))

        self.supernode_count = self.supernodes_per_partition_count * self.partition_count
        # v's per sn divided by max incoming edges per iv's , rounded up, multipled by total amount of supernodes
        self.total_intermediary_v_count = int(math.ceil(self.adj_v_per_supernode / self.intermediary_v_per_sn_count)) * self.supernode_count  

        self.total_v_count = self.supernodes_per_partition_count * self.adj_v_per_supernode * self.partition_count + self.total_intermediary_v_count

        # for now, the same. One e per v, except the supernodes themselves don't have an edge
        # TODO calculate. Needs to add 2 edges per intermediary node
        #self.total_e_count = self.total_v_count - self.supernodes_per_partition_count


        self.tmp_data_path = self.data_dir_path

        self.edges_csv_filename = os.path.join(self.tmp_data_path, f"edges.csv")
        self.intermediary_vertices_csv_filename = os.path.join(self.tmp_data_path, f"intermediary-vertices.csv")

        self.intermediary_edges_csv_filename = os.path.join(self.tmp_data_path, f"intermediary-edges.csv")
        self.intermediary_uuids_txt_filename = os.path.join(self.tmp_data_path, f"intermediarys-uuids.txt")

        self.supernodes_uuids_txt_filename = os.path.join(self.tmp_data_path, f"supernodes_uuids.txt")

    def generate_vertex_info(self, partition_key="dont-bother-this-script-is-for-67"):
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

    def move_to_next_intermediary_v(self):
        """
        - called by generate_intermediary_edges everytime you switch to a new intermediary vertex
        """
        self.current_iv = self.remaining_intermediary_vertices.pop()

        print(f"We have  {len(self.remaining_intermediary_vertices)}/{self.total_intermediary_v_count} intermediary vertices left to build edges for")
        self.current_count_for_iv = 0

        # write an edge for this intermediary vertex and the supernode
        with open(self.intermediary_edges_csv_filename, 'a') as ieFile:
            ieWriter = csv.writer(ieFile, delimiter = '|')
            iv_to_sn = (self.current_iv["uuid"], self.current_supernode_uuid, "intermediary node to supernode")
            ieWriter.writerow(iv_to_sn)

    def generate_intermediary_edges(self):
        """
        - supernodes are already generated at thispoint. 
        - Now generate adjacent vertices and their edges
        """

        # keep track of intermediary_vertices that are left to use 
        self.remaining_intermediary_vertices = list.copy(self.intermediary_vertices)
        total_intermediary_vertices =  len(self.intermediary_vertices)

        if self.total_intermediary_v_count != total_intermediary_vertices:
            # should never get this, it means our code is wrong
            print(f"{total_intermediary_vertices} != {self.total_intermediary_v_count}   (but it should)")
            print("Didn't calculate correctly, try again")
            return

        with open(self.intermediary_vertices_csv_filename, 'a') as ivFile, open(self.intermediary_edges_csv_filename, 'a') as ieFile, open(self.edges_csv_filename, 'r') as main_edges_file:

            ivWriter = csv.writer(ivFile, delimiter = '|')
            ieWriter = csv.writer(ieFile, delimiter = '|')
            main_edges_reader = csv.DictReader(main_edges_file, delimiter='|')

            # iterate over the already existing edges, and assign each one to an iv
            for edge_line in main_edges_reader:

                #################################
                #1) set the uuid values from the original edge
                connected_v_uuid = edge_line["out_uuid"]
                supernode_v_uuid = edge_line["in_uuid"]

                #################################
                # 2) check if we need a new intermediary vertex for this edge
                if (
                    self.current_count_for_iv == self.edges_per_intermediary_v
                ) or (
                    supernode_v_uuid != self.current_supernode_uuid
                ):
                    # reached max edges for this iv, go to next iv before going on to next edge
                    print(f"reached max for this intermediary edge, because {self.current_count_for_iv} == {self.edges_per_intermediary_v}")
                    print(f"OR , because {supernode_v_uuid} != {self.current_supernode_uuid}")
                    # NOTE might not make any change at all, depends on why we're in this conditional code block
                    self.current_supernode_uuid = supernode_v_uuid

                    self.move_to_next_intermediary_v()



                #################################
                # 3) make edge from small vertex to intermediary vertex
                # - note that it goes from connected v -> intermediary v -> supernode, IN THAT ORDER. MAKE SURE IT'S IN THAT ORDER.
                ieWriter.writerow((connected_v_uuid, self.current_iv["uuid"], "small node to intermediary-node"))

                # 4) increment count
                self.current_count_for_iv = self.current_count_for_iv + 1

        # finished
        print(f"We have  {len(self.remaining_intermediary_vertices)}/{self.total_intermediary_v_count} intermediary vertices left to build edges for")





    def generate_intermediary_vertices(self):
        """
        """

        with open(self.intermediary_vertices_csv_filename, 'a') as iv_csvFile, open(self.intermediary_uuids_txt_filename, 'w') as in_txtFile:
            iv_writer = csv.writer(iv_csvFile, delimiter = '|')

            for supernode_uuid in self.supernode_uuids:

                for i in range(self.intermediary_v_per_sn_count):
                    intermediary_v = self.generate_vertex_info()
                    # put into memory. Should be relatively small number, so safe to put in memory

                    self.intermediary_vertices.append(intermediary_v)

                    # write to csv as vertex
                    # - create tuple of data
                    data_to_write = (intermediary_v[header] for header in self.vertices_headers)
                    # - write to row
                    iv_writer.writerow(data_to_write)

                    # write uuid down for this sn
                    in_txtFile.write(str(intermediary_v["uuid"]) + "\n")

    

    def initialize_csv_files(self):
        """
        - write headers for both csvs
        """

        # for vertices
        # note that w mode will clear existing lines in file if exists
        with open(self.intermediary_vertices_csv_filename, 'w') as csvFile:
            v_writer = csv.writer(csvFile, delimiter = '|')
            v_writer.writerow(self.vertices_headers)

        # for edges
        # note that w mode will clear existing lines in file if exists
        with open(self.intermediary_edges_csv_filename, 'w') as csvFile:
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
        
        vertices_file_size = os.path.getsize(self.intermediary_vertices_csv_filename)
        edges_file_size = os.path.getsize(self.intermediary_edges_csv_filename)
        print("\n====================\nMetrics:")
        print("====================")
        print("partition count:", self.partition_count)
        print("supernodes per partition count:", self.supernodes_per_partition_count)
        print("adjacent vertices per supernode count:", self.adj_v_per_supernode)
        print("Max. outgoing edges per intermediary vertex:", self.edges_per_intermediary_v)
        print("total intermediary vertices count:", self.total_intermediary_v_count)
        #print("total edges count:", self.total_e_count)
        print("== intermediary vertices file size:", self.convert_size(vertices_file_size))
        print("== edges file size:", self.convert_size(edges_file_size))

    def set_supernodes(self):
        """
        read the plaintext uuids of the supernodes and put in memory
        """
        with open(self.supernodes_uuids_txt_filename, 'r') as sn_txtFile:
            self.supernode_uuids = [line.rstrip() for line in sn_txtFile]



    def main(self):
        self.initialize_csv_files()
        self.set_supernodes()
        self.generate_intermediary_vertices()
        self.generate_intermediary_edges()
        print("done.\n")
        self.print_file_metrics()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            usage=' <path-to-data-dir> <max-incoming-edges-for-intermediary-vertex>')

    parser.add_argument('data_dir_path', type=str, help='relative path to the csv', default=2)
    parser.add_argument('edges_per_intermediary_v', type=str, help='Maximum incoming edges in a given intermediary vertex after we divide it up with this script. defaults to 1000', default=1000)

    args = parser.parse_args()

    data_dir_path = args.data_dir_path
    edges_per_intermediary_v = int(args.edges_per_intermediary_v)


    generator = IntermediaryNodeGenerator(data_dir_path, edges_per_intermediary_v)
    generator.main()

