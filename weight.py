import argparse
import os

import yaml

from pivotal_product import PivotalProduct

parser = argparse.ArgumentParser()
parser.add_argument("--file-path", help="path to your .pivotal file")

args = parser.parse_args()
print(args)

product_size = os.path.getsize(args.file_path)

pp = PivotalProduct(args.file_path)

print(pp.get_product_name())
print(pp.get_product_version())

for release in pp.get_releases():
    print(yaml.dump(pp.get_release_manifest(release), default_flow_style=False))
