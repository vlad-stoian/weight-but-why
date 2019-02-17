import os.path
import tarfile
import zipfile

import yaml


class BoshRelease:
    @staticmethod
    def from_manifest(manifest, file_size, compress_size):
        return BoshRelease(
            manifest["name"],
            manifest["version"],
            file_size=file_size,
            compress_size=compress_size,
        )

    def __init__(self, name, version, file_size=None, compress_size=None):
        self._name = name
        self._version = version
        self._file_size = file_size
        self._compress_size = compress_size

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def file_size(self):
        return self._file_size

    @property
    def compress_size(self):
        return self._compress_size

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def _find_manifest(release_tar):
    for release_file in release_tar:
        if release_file.name.endswith("release.MF"):
            release_manifest_file = release_tar.extractfile(release_file)
            return yaml.load(release_manifest_file.read())
    raise LookupError("couldn't find 'release.MF' file")


def parse_product(product_file_path):
    if not os.path.isfile(product_file_path):
        raise ValueError("{} is not a file".format(product_file_path))

    if not zipfile.is_zipfile(product_file_path):
        raise ValueError("{} is not a zip file".format(product_file_path))

    product_file_size = os.path.getsize(product_file_path)

    product_zip = zipfile.ZipFile(product_file_path)
    metadata_zipinfo = product_zip.getinfo("metadata/metadata.yml")
    metadata_file = product_zip.open(metadata_zipinfo)
    metadata = yaml.load(metadata_file)

    pp = PivotalProduct.from_metadata(metadata, product_file_size)

    releases = [
        pf for pf in product_zip.infolist() if pf.filename.startswith("releases")
    ]

    for release in releases:
        release_tar_file = product_zip.open(release)
        release_tar = tarfile.open(mode="r:gz", fileobj=release_tar_file)

        release_manifest = _find_manifest(release_tar)

        pp.add_release(
            BoshRelease.from_manifest(
                release_manifest, release.file_size, release.compress_size
            )
        )

    return pp


class PivotalProduct:
    @staticmethod
    def from_metadata(metadata, file_size):
        return PivotalProduct(metadata["name"], metadata["product_version"], file_size)

    def __init__(self, name, version, file_size=None):
        self._name = name
        self._version = version
        self._file_size = file_size
        self._releases = []

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def file_size(self):
        return self._file_size

    @property
    def releases(self):
        return self._releases

    def add_release(self, release):
        self._releases.append(release)
