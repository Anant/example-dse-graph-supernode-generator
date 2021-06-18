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
    - ALWAYS deletes old data 

    Warnings: 
    - due to use of range, make sure to use python3 for performance reasons

    """
    supernodes = []
    tmp_data_path = os.path.join(current_file_abs_path, "../tmp/data")
    vertices_csv_filename = os.path.join(tmp_data_path, "vertices.csv")
    edges_csv_filename = os.path.join(tmp_data_path, "edges.csv")

    vertices_headers = ["uuid", "name", "info"]
    edges_headers = ["source_uuid", "target_uuid"]

    def __init__(self, supernode_count, records_per_supernode_count):
        self.supernode_count = supernode_count
        self.records_per_supernode_count = records_per_supernode_count

    def generate_vertex_info(self):
        """
        generates the data to be written to CSV row for a single row
        - for now incrementing integer works fine
        """
        
        return {
            "uuid": uuid.uuid4(),
            "name": fake.name(),
            "info": fake.sentence()
            }

    def generate_other_vertices_with_edges(self):
        with open(self.vertices_csv_filename, 'a') as vFile, open(self.edges_csv_filename, 'a') as eFile:
            vWriter = csv.writer(vFile, delimiter = '|')
            eWriter = csv.writer(eFile, delimiter = '|')

            for supernode in self.supernodes:
                # TODO might do this differently so we don't have to have as much in memory. But I think this is faster for file IO since it has 
                for i in range(self.records_per_supernode_count):

                    ##############################
                    # make vertex
                    connected_v = self.generate_vertex_info()

                    # write to csv as vertex
                    # - create tuple of data
                    v_data_to_write = (connected_v[header] for header in self.vertices_headers)
                    # - write to row
                    vWriter.writerow(v_data_to_write)

                    ##############################
                    # make edge connecting it to supernode
                    # source then target
                    # e.g., Fan123 likes JustinBieber (the supernode)
                    e_data_to_write = (connected_v["uuid"], supernode["uuid"])
                    eWriter.writerow(e_data_to_write)


    def generate_supernode_vertices(self):
        """
        - note that the output will not be actual supernode yet, just the vertices for the super nodes
        """
        with open(self.vertices_csv_filename, 'a') as csvFile:
            v_writer = csv.writer(csvFile, delimiter = '|')

            for i in range(self.supernode_count):
                supernode_v = self.generate_vertex_info()
                # put into memory. Should be small number, so safe to put in memory
                self.supernodes.append(supernode_v)

                # write to csv as vertex
                # - create tuple of data
                data_to_write = (supernode_v[header] for header in self.vertices_headers)
                # - write to row
                v_writer.writerow(data_to_write)
    

    def initialize_csv_files(self):
        """
        - write headers for both csvs
        """

        # remove existing data and make tmp dir
        if not os.path.exists(self.tmp_data_path):
            Path(self.tmp_data_path).mkdir(parents=True, exist_ok=True)

        # for vertices
        # note that wt will clear existing lines in file if exists
        with open(self.vertices_csv_filename, 'wt') as csvFile:
            v_writer = csv.writer(csvFile, delimiter = '|')
            v_writer.writerow(self.vertices_headers)

        # for edges
        # note that wt will clear existing lines in file if exists
        with open(self.edges_csv_filename, 'wt') as csvFile:
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
            usage=' <supernode_count> <total_count>')

    parser.add_argument('supernode_count', type=str, help='defaults to 2', default=2)
    parser.add_argument('records_per_supernode_count', type=str, help='defaults to 10', default=10)

    args = parser.parse_args()

    # number of supernodes
    supernode_count = int(args.supernode_count)
    # records will be evenly distributed between supernodes
    records_per_supernode_count = int(args.records_per_supernode_count)

    generator = Generator(supernode_count, records_per_supernode_count)
    generator.main()

    print("CSV generation complete!")
