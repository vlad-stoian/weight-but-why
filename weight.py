import argparse
import os
from zipfile import ZipFile


parser = argparse.ArgumentParser()
parser.add_argument("file_path", help="path to your .pivotal file")
args = parser.parse_args()

# check file exists
# check file is a zip

with ZipFile(args.file_path) as pzip:
    for zfile in pzip.infolist():
        if not zfile.is_dir() and "release" in zfile.filename:
            product="p-rabbitmq"
            release=os.path.basename(zfile.filename)
            release=release.rpartition('-')[0]

            tags="release:{},product:{}".format(release,product)



            print("dog metric post --host iMac --tags {} --type gauge vstoian.p-rabbitmq.size {}".format(tags, zfile.file_size))

