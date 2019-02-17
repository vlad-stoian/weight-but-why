import zipfile
import yaml
import tarfile
import os.path


class BoshRelease:
    def __init__(self):
        pass


class PivotalProduct:
    @staticmethod
    def parse_product(product_path):
        if not os.path.isfile(product_path):
            raise ValueError("{} is not a file".format(product_path))

        if not zipfile.is_zipfile(product_path):
            raise ValueError("{} is not a zip file".format(product_path))

    def __init__(self, product_path):
        self.product_file_path = product_path

    def get_product_file_path(self):
        return self.product_file_path

    @property
    def product_version(self):
        product_zip = zipfile.ZipFile(self.product_file_path)
        metadata_zipinfo = product_zip.getinfo("metadata/metadata.yml")
        metadata_file = product_zip.open(metadata_zipinfo)
        metadata = yaml.load(metadata_file)

        return metadata["product_version"]

    @property
    def product_name(self):
        product_zip = zipfile.ZipFile(self.product_file_path)
        metadata_zipinfo = product_zip.getinfo("metadata/metadata.yml")
        metadata_file = product_zip.open(metadata_zipinfo)
        metadata = yaml.load(metadata_file)

        return metadata["name"]

    @property
    def releases(self):
        releases = []

        self.product_zip = zipfile.ZipFile(self.product_file_path)

        for product_file in self.product_zip.infolist():

            if product_file.filename.startswith("releases"):
                releases.append(product_file.filename)

        return releases

    def get_release_manifest(self, release_name):

        product_zip = zipfile.ZipFile(self.product_file_path)
        metadata_zipinfo = product_zip.getinfo(release_name)

        release_tar_file = product_zip.open(metadata_zipinfo)
        release_tar = tarfile.open(mode="r:gz", fileobj=release_tar_file)

        for file_in_tar in release_tar:
            if file_in_tar.name.endswith("release.MF"):
                release_manifest_file = release_tar.extractfile(file_in_tar)
                return yaml.load(release_manifest_file.read())

        raise Exception("Jesus")
