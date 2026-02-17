import io
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Generator

import pytest
import yaml

from pivotal_product import BoshRelease, parse_product


class TestBoshRelease:
    def test_properties_only_needed(self) -> None:
        br = BoshRelease("random-name", "random-version")

        assert br.name == "random-name"
        assert br.version == "random-version"
        assert br.file_size is None
        assert br.compress_size is None

    def test_properties_all(self) -> None:
        br = BoshRelease("random-name", "random-version", 1234, 5678)

        assert br.name == "random-name"
        assert br.version == "random-version"
        assert br.file_size == 1234
        assert br.compress_size == 5678

    def test_from_manifest(self) -> None:
        manifest = {"name": "name-from-manifest", "version": "version-from-manifest"}
        br = BoshRelease.from_manifest(manifest, 1234, 5678)

        assert br.name == "name-from-manifest"
        assert br.version == "version-from-manifest"
        assert br.file_size == 1234
        assert br.compress_size == 5678


@pytest.fixture
def product_file() -> Generator[Path, None, None]:
    product_metadata = {"product_version": "1.2.3.4.5", "name": "the-product"}

    release1_metadata = {"name": "release-1-name", "version": "release-1-version"}
    release2_metadata = {"name": "release-2-name", "version": "release-2-version"}

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        pivotal_file = temp_path / "product.pivotal"

        with zipfile.ZipFile(pivotal_file, "w", compression=zipfile.ZIP_STORED) as zf:
            zf.writestr(
                "metadata/metadata.yml",
                yaml.dump(product_metadata, default_flow_style=False),
            )

            for i, meta in enumerate([release1_metadata, release2_metadata], 1):
                tgz_name = f"release-{i}.tgz"
                tgz_path = temp_path / tgz_name

                with tarfile.open(tgz_path, "w:gz") as tar:
                    manifest_content = yaml.dump(meta, default_flow_style=False).encode(
                        "utf-8"
                    )
                    ti = tarfile.TarInfo("release.MF")
                    ti.size = len(manifest_content)
                    tar.addfile(ti, io.BytesIO(manifest_content))

                zf.write(tgz_path, arcname=f"releases/{tgz_name}")

        yield pivotal_file


def test_parse_product(product_file: Path) -> None:
    pp = parse_product(product_file)

    assert pp.version == "1.2.3.4.5"
    assert pp.name == "the-product"
    assert len(pp.releases) == 2

    # Verify releases are sorted or order preserved?
    # ZipFile.infolist() order depends on insertion order usually.
    # I inserted release-1 then release-2.
    # But checking by name is safer if order is not guaranteed.

    r1 = next(r for r in pp.releases if r.name == "release-1-name")
    assert r1.version == "release-1-version"

    r2 = next(r for r in pp.releases if r.name == "release-2-name")
    assert r2.version == "release-2-version"
