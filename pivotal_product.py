import tarfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import yaml


@dataclass
class BoshRelease:
    name: str
    version: str
    file_size: int | None = None
    compress_size: int | None = None

    @classmethod
    def from_manifest(
        cls, manifest: dict[str, Any], file_size: int, compress_size: int
    ) -> "BoshRelease":
        return cls(
            name=manifest["name"],
            version=manifest["version"],
            file_size=file_size,
            compress_size=compress_size,
        )


@dataclass
class PivotalProduct:
    name: str
    version: str
    file_size: int | None = None
    releases: list[BoshRelease] = field(default_factory=list)

    @classmethod
    def from_metadata(
        cls, metadata: dict[str, Any], file_size: int
    ) -> "PivotalProduct":
        return cls(
            name=metadata["name"],
            version=metadata["product_version"],
            file_size=file_size,
        )

    def add_release(self, release: BoshRelease) -> None:
        self.releases.append(release)


def _find_manifest(release_tar: tarfile.TarFile) -> dict[str, Any]:
    for release_file in release_tar:
        if release_file.name.endswith("release.MF"):
            release_manifest_file = release_tar.extractfile(release_file)
            if release_manifest_file:
                return cast(
                    dict[str, Any], yaml.safe_load(release_manifest_file.read())
                )
    raise LookupError("couldn't find 'release.MF' file")


def parse_product(product_file_path: str | Path) -> PivotalProduct:
    path = Path(product_file_path)
    if not path.is_file():
        raise ValueError(f"{path} is not a file")

    if not zipfile.is_zipfile(path):
        raise ValueError(f"{path} is not a zip file")

    product_file_size = path.stat().st_size

    with zipfile.ZipFile(path) as product_zip:
        metadata_zipinfo = product_zip.getinfo("metadata/metadata.yml")
        with product_zip.open(metadata_zipinfo) as metadata_file:
            metadata = cast(dict[str, Any], yaml.safe_load(metadata_file))

        pp = PivotalProduct.from_metadata(metadata, product_file_size)

        releases = [
            pf for pf in product_zip.infolist() if pf.filename.startswith("releases")
        ]

        for release in releases:
            with product_zip.open(release) as release_tar_file:
                with tarfile.open(mode="r:gz", fileobj=release_tar_file) as release_tar:
                    release_manifest = _find_manifest(release_tar)

                    pp.add_release(
                        BoshRelease.from_manifest(
                            release_manifest, release.file_size, release.compress_size
                        )
                    )

    return pp
