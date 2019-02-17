import tarfile
import tempfile
import unittest
from zipfile import ZipFile, ZIP_STORED

import yaml

from pivotal_product import PivotalProduct, BoshRelease, parse_product


class TestBoshRelease(unittest.TestCase):
    def test_properties_only_needed(self):
        br = BoshRelease("random-name", "random-version")

        self.assertEqual("random-name", br.name, "name doesn't match")
        self.assertEqual("random-version", br.version, "version doesn't match")
        self.assertIsNone(br.file_size, "file size is not None")
        self.assertIsNone(br.compress_size, "compress size is not None")

    def test_properties_all(self):
        br = BoshRelease("random-name", "random-version", 1234, 5678)

        self.assertEqual("random-name", br.name, "name doesn't match")
        self.assertEqual("random-version", br.version, "version doesn't match")
        self.assertEqual(1234, br.file_size, "file_size doesn't match")
        self.assertEqual(5678, br.compress_size, "compress_size doesn't match")

    def test_from_manifest(self):
        manifest = {"name": "name-from-manifest", "version": "version-from-manifest"}
        br = BoshRelease.from_manifest(manifest, 1234, 5678)

        self.assertEqual("name-from-manifest", br.name, "name doesn't match")
        self.assertEqual("version-from-manifest", br.version, "version doesn't match")
        self.assertEqual(1234, br.file_size, "file_size doesn't match")
        self.assertEqual(5678, br.compress_size, "compress_size doesn't match")


class TestPivotalProduct(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._product_file_path = tempfile.NamedTemporaryFile(delete=False).name

        product_metadata = {"product_version": "1.2.3.4.5", "name": "the-product"}

        release1_metadata = {"name": "release-1-name", "version": "release-1-version"}
        release2_metadata = {"name": "release-2-name", "version": "release-2-version"}

        with ZipFile(cls._product_file_path, "w", compression=ZIP_STORED) as temp_zip:
            temp_zip.writestr(
                "metadata/metadata.yml",
                yaml.dump(product_metadata, default_flow_style=False),
            )

            with tarfile.open("release-1.tgz", "w:gz") as tar:
                with tempfile.NamedTemporaryFile(mode="w", delete=False) as fp:
                    fp.write(yaml.dump(release1_metadata, default_flow_style=False))
                tar.add(fp.name, arcname="release.MF")
            temp_zip.write(tar.name, arcname="releases/release-1.tgz")

            with tarfile.open("release-2.tgz", "w:gz") as tar:
                with tempfile.NamedTemporaryFile(mode="w", delete=False) as fp:
                    fp.write(yaml.dump(release2_metadata, default_flow_style=False))
                tar.add(fp.name, arcname="./release.MF")
            temp_zip.write(tar.name, arcname="releases/release-2.tgz")

        print("[setUp] created file", cls._product_file_path)

    @classmethod
    def tearDownClass(cls):
        pass
        # os.remove(cls._product_file_path)

    def setUp(self):
        self.pivotal_product = parse_product(self.__class__._product_file_path)

    def test_get_product_version(self):
        self.assertEqual(
            "1.2.3.4.5", self.pivotal_product.version, "product version doesn't match"
        )

    def test_get_product_name(self):
        self.assertEqual(
            "the-product", self.pivotal_product.name, "product name doesn't match"
        )

    def test_get_releases(self):
        self.assertEqual("release-1-name", self.pivotal_product.releases[0].name)
        self.assertEqual("release-1-version", self.pivotal_product.releases[0].version)

        self.assertEqual("release-2-name", self.pivotal_product.releases[1].name)
        self.assertEqual("release-2-version", self.pivotal_product.releases[1].version)


if __name__ == "__main__":
    unittest.main()
