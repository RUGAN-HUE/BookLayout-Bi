"""Validate the pixel-free BookLayout-Bi release package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


EXPECTED = {
    "records": 10_161,
    "stage1_train": 8_971,
    "stage1_validation": 996,
    "stage2_train": 1_572,
    "stage2_validation": 174,
    "test": 194,
}
FORBIDDEN_RECORD_KEYS = {"image_path", "imagePath", "imageData", "source_local_path"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff"}
HEX_16 = re.compile(r"^[0-9a-f]{16}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")


def read_ids(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    assert hashlib.sha256((root / "LICENSE").read_bytes()).hexdigest() == (
        "3711f963c05d0be80d53e5923308a6dee31b203da23435c9cfb7c7b6e4dd5e19"
    )
    assert hashlib.sha256(
        (root / "LICENSES" / "PolyForm-Noncommercial-1.0.0.md").read_bytes()
    ).hexdigest() == "ff67ab0c08d545dc4e5dac0f072807eb6c5002c1ed1c3de7093e1eaa0b02d298"
    license_text = (root / "LICENSE").read_text(encoding="utf-8")
    assert "Attribution-NonCommercial 4.0 International" in license_text
    license_scope = (root / "LICENSE_SCOPE.md").read_text(encoding="utf-8")
    assert "Commercial use" in license_scope
    assert "do **not** apply to the underlying book-cover artwork" in license_scope
    annotation_path = root / "data" / "booklayout_bi_annotations.json"
    with annotation_path.open("r", encoding="utf-8") as stream:
        records = json.load(stream)["records"]

    assert len(records) == EXPECTED["records"]
    record_ids = [record["sample_id"] for record in records]
    assert len(record_ids) == len(set(record_ids))
    by_id = {record["sample_id"]: record for record in records}
    for record in records:
        assert not FORBIDDEN_RECORD_KEYS.intersection(record)
        assert record["num_elements"] == len(record["elements"]) >= 1
        for element in record["elements"]:
            box = element["bbox_xyxy_normalized"]
            assert len(box) == 4
            assert all(0.0 <= value <= 1.0 for value in box)
            assert box[0] <= box[2] and box[1] <= box[3]

    split_root = root / "data" / "splits"
    splits = {
        name: read_ids(split_root / f"{name}.txt")
        for name in EXPECTED
        if name != "records"
    }
    for name, ids in splits.items():
        assert len(ids) == EXPECTED[name]
        assert len(ids) == len(set(ids))
        assert set(ids).issubset(by_id)

    manifest_path = root / "statistics" / "split_manifest.json"
    with manifest_path.open("r", encoding="utf-8") as stream:
        split_manifest = json.load(stream)["files"]
    assert set(split_manifest) == {f"{name}.txt" for name in splits}
    for name in splits:
        filename = f"{name}.txt"
        split_path = split_root / filename
        entry = split_manifest[filename]
        assert entry["records"] == EXPECTED[name]
        digest = hashlib.sha256(split_path.read_bytes()).hexdigest()
        assert digest == entry["sha256"]

    test = set(splits["test"])
    stage1_train = set(splits["stage1_train"])
    stage1_validation = set(splits["stage1_validation"])
    stage2_train = set(splits["stage2_train"])
    stage2_validation = set(splits["stage2_validation"])
    assert not test.intersection(stage1_train | stage1_validation | stage2_train | stage2_validation)
    assert not stage1_train.intersection(stage1_validation)
    assert stage1_train | stage1_validation | test == set(record_ids)
    assert not stage2_train.intersection(stage2_validation)
    assert stage2_train | stage2_validation | test == {
        sample_id
        for sample_id, record in by_id.items()
        if record["annotation_type"] == "manual"
    }

    provenance_path = root / "data" / "provenance.csv"
    with provenance_path.open("r", encoding="utf-8-sig", newline="") as stream:
        provenance = list(csv.DictReader(stream))
    assert len(provenance) == EXPECTED["records"]
    provenance_ids = [row["sample_id"] for row in provenance]
    assert len(provenance_ids) == len(set(provenance_ids))
    assert set(provenance_ids) == set(record_ids)
    for row in provenance:
        assert HEX_16.fullmatch(row["phash_64"])
        assert HEX_64.fullmatch(row["sha256"])
        source_url = row["source_url"]
        assert not source_url or source_url.startswith(("http://", "https://"))
        serialized = "|".join(row.values())
        assert not re.search(r"(?:^|[|])(?:[A-Za-z]:\\|/home/|/Users/)", serialized)

    image_files = [path for path in root.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS]
    assert not image_files, image_files[:5]
    print("BookLayout-Bi validation: PASS")


if __name__ == "__main__":
    main()
