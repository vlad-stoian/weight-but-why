import argparse
import os

from beeprint import pp

import pivotal_product

parser = argparse.ArgumentParser()
parser.add_argument("--file-path", help="path to your .pivotal file")

args = parser.parse_args()
print(args)

product_size = os.path.getsize(args.file_path)

product = pivotal_product.parse_product(args.file_path)

pp(product)
