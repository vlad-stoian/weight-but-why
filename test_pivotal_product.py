import tarfile
import tempfile
import unittest
from zipfile import ZipFile

import yaml

from pivotal_product import PivotalProduct


class TestPivotalProduct(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._product_file_path = tempfile.NamedTemporaryFile(delete=False).name

        product_metadata = {"product_version": "1.2.3.4.5", "name": "the-product"}

        release1_metadata = {"name": "release-1-name", "version": "release-1-version"}
        release2_metadata = {"name": "release-2-name", "version": "release-2-version"}

        with ZipFile(cls._product_file_path, "w") as temp_zip:
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
        self.pivotal_product = PivotalProduct(self.__class__._product_file_path)

    def test_get_product_file_path(self):
        self.assertEqual(
            "some-path",
            PivotalProduct("some-path").get_product_file_path(),
            "product path should be the same",
        )

    def test_get_product_version(self):
        self.assertEqual(
            "1.2.3.4.5",
            self.pivotal_product.get_product_version(),
            "product version doesn't match",
        )

    def test_get_product_name(self):
        self.assertEqual(
            "the-product",
            self.pivotal_product.get_product_name(),
            "product name doesn't match",
        )

    def test_get_releases(self):
        self.assertEqual(
            ["releases/release-1.tgz", "releases/release-2.tgz"],
            self.pivotal_product.get_releases(),
            "releases don't match",
        )

    def test_get_release_manifest(self):
        release_manifest = self.pivotal_product.get_release_manifest(
            "releases/release-1.tgz"
        )

        self.assertEqual(
            "release-1-name", release_manifest["name"], "release name doesn't match"
        )
        self.assertEqual(
            "release-1-version",
            release_manifest["version"],
            "release version doesn't match",
        )


if __name__ == "__main__":
    unittest.main()
