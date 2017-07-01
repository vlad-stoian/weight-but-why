import argparse
import os
import tempfile
import tarfile
from zipfile import ZipFile


parser = argparse.ArgumentParser()
parser.add_argument("file_path", help="path to your .pivotal file")
args = parser.parse_args()

metrics_prefix = "vstoian.test.1"
metrics_host = "iMac"

# check file exists
# check file is a zip

temp_dir = tempfile.mkdtemp()

product_name = ""
product_version = ""
product_size = os.path.getsize(args.file_path)

product_releases = []

with tempfile.TemporaryDirectory() as temp_dir:
    zip_ref = ZipFile(args.file_path, 'r')
    zip_ref.extractall(temp_dir)
    zip_ref.close()


    for dir_name, subdirs, files in os.walk(temp_dir):
        if dir_name.endswith("metadata"):
            if len(files) < 1:
                raise Exception("Metadata folder is empty")
            metadata_file_path = os.path.join(dir_name, files[0])

            with open(metadata_file_path, 'r') as metadata_file:
                for line in metadata_file.readlines():
                    if line.startswith("name: "):
                        product_name = line.split(' ')[1].strip().strip('\'').strip('\"')
                    if line.startswith("product_version: "):
                        product_version = line.split(' ')[1].strip().strip('\'').strip('\"')

        if dir_name.endswith("releases"):
            for release_file_name in files:
                release_file_path = os.path.join(dir_name, release_file_name)

                release_name = ""
                release_version = ""
                release_size = os.path.getsize(release_file_path)

                with tempfile.TemporaryDirectory() as release_temp_dir:
                    with tarfile.open(release_file_path, 'r:gz') as release_tar:
                        release_tar.extractall(release_temp_dir)

                    release_manifest_path = os.path.join(release_temp_dir, 'release.MF')
                    with open(release_manifest_path) as release_manifest_file:
                        for line in release_manifest_file.readlines():
                            if line.startswith("name: "):
                                release_name = line.split(' ')[1].strip().strip('\'').strip('\"')
                            if line.startswith("version: "):
                                release_version = line.split(' ')[1].strip().strip('\'').strip('\"')

                product_releases.append({'name': release_name, 'version': release_version, 'size': release_size})


# print(product_name)
# print(product_version)
# print(product_size)
# print(product_releases)


print("dog metric post --host {} --tags version:{} --type gauge {}.{}.size {}".format(metrics_host, product_version, metrics_prefix, product_name, product_size))

for release in product_releases:
    print("dog metric post --host {} --tags release:{},version:{} --type gauge {}.{}.releases {}".format(metrics_host, release['name'], release['version'], metrics_prefix, product_name, release['size']))

