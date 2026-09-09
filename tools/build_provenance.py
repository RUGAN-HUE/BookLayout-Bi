"""Build a pixel-free provenance table for BookLayout-Bi.

The generated CSV contains no image bytes or local filesystem paths. It joins
stable public sample identifiers to perceptual/content hashes and, where an
unambiguous Book32 record is recoverable, the original public source URL.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image


def public_id(record: dict) -> str:
    key = "|".join(
        str(record.get(field, ""))
        for field in ("language", "category", "annotation_type", "stem")
    )
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16].upper()
    return f"BLB-{digest}"


def read_rename_log(path: Path) -> dict[tuple[str, str], str]:
    mapping: dict[tuple[str, str], str] = {}
    with path.open(
        "r", encoding="utf-8-sig", errors="replace", newline=""
    ) as stream:
        for row in csv.DictReader(stream):
            key = (row["category"].strip().casefold(), row["new_name"].strip().casefold())
            if key in mapping:
                raise ValueError(f"Duplicate rename key: {key}")
            mapping[key] = row["original_name"].strip()
    return mapping


def normalized_book_key(value: str) -> str:
    stem = Path(value).stem.strip().casefold()
    stripped = stem.lstrip("0")
    return stripped or "0"


def read_book32(
    path: Path,
) -> tuple[dict[str, dict[str, str]], dict[str, list[dict[str, str]]]]:
    by_filename: dict[str, dict[str, str]] = {}
    by_normalized_key: dict[str, list[dict[str, str]]] = {}
    with path.open(
        "r", encoding="utf-8-sig", errors="replace", newline=""
    ) as stream:
        for row in csv.reader(stream):
            if len(row) < 3:
                continue
            record = {
                "book_id": row[0].strip(),
                "filename": row[1].strip(),
                "url": row[2].strip(),
            }
            key = record["filename"].casefold()
            if key in by_filename and by_filename[key] != record:
                raise ValueError(f"Conflicting Book32 filename: {record['filename']}")
            by_filename[key] = record
            for candidate in {record["filename"], record["book_id"]}:
                norm = normalized_book_key(candidate)
                bucket = by_normalized_key.setdefault(norm, [])
                if record not in bucket:
                    bucket.append(record)
    return by_filename, by_normalized_key


def dct_matrix(size: int) -> np.ndarray:
    matrix = np.empty((size, size), dtype=np.float64)
    factor = math.pi / (2.0 * size)
    scale0 = math.sqrt(1.0 / size)
    scale = math.sqrt(2.0 / size)
    for frequency in range(size):
        row_scale = scale0 if frequency == 0 else scale
        for position in range(size):
            matrix[frequency, position] = row_scale * math.cos(
                (2 * position + 1) * frequency * factor
            )
    return matrix


DCT_32 = dct_matrix(32)


def phash64(path: Path) -> str:
    with Image.open(path) as image:
        grayscale = image.convert("L").resize((32, 32), Image.Resampling.LANCZOS)
        pixels = np.asarray(grayscale, dtype=np.float64)
    coefficients = DCT_32 @ pixels @ DCT_32.T
    low_frequency = coefficients[:8, :8]
    threshold = float(np.median(low_frequency))
    bits = (low_frequency > threshold).reshape(-1)
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    return f"{value:016x}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--source-json", type=Path, required=True)
    parser.add_argument("--book32-listing", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--output-statistics", type=Path, required=True)
    args = parser.parse_args()

    with args.source_json.open("r", encoding="utf-8") as stream:
        source_records = json.load(stream)["records"]
    records = [record for record in source_records if int(record.get("num_elements", 0)) >= 1]
    if len(source_records) != 10_171 or len(records) != 10_161:
        raise ValueError(
            f"Unexpected record counts: source={len(source_records)}, valid={len(records)}"
        )

    rename_logs = {
        "english": read_rename_log(
            args.project_root / "English_Final_5000data" / "rename_log.csv"
        ),
        "chinese": read_rename_log(
            args.project_root / "Chinese_Final_5000data" / "rename_log_chinese.csv"
        ),
    }
    book32_exact, book32_normalized = read_book32(args.book32_listing)

    rows: list[dict[str, str]] = []
    counts = Counter()
    phash_counts = Counter()
    sha256_counts = Counter()

    for index, record in enumerate(records, start=1):
        sample_id = public_id(record)
        language = str(record["language"])
        image_relative = Path(record["image_path"])
        image_path = args.project_root / image_relative
        if not image_path.is_file():
            raise FileNotFoundError(image_path)

        original_name = rename_logs[language].get(
            (str(record["category"]).casefold(), image_relative.name.casefold())
        )
        if not original_name:
            raise ValueError(f"No rename-log entry for {sample_id}")

        source_collection = (
            "Book Dataset - Task 2 (Book32)"
            if language == "english"
            else "Official websites of eight Chinese publishers"
        )
        source_record_id = ""
        source_url = ""
        source_url_status = "not_retained"

        if language == "english":
            source = book32_exact.get(original_name.casefold())
            match_method = "exact_filename"
            if source is None:
                candidates = book32_normalized.get(normalized_book_key(original_name), [])
                if len(candidates) == 1:
                    source = candidates[0]
                    match_method = "unique_normalized_identifier"
                else:
                    match_method = "not_recovered"
            if source is not None and source["url"]:
                source_record_id = source["book_id"]
                source_url = source["url"]
                source_url_status = match_method
                counts["english_url_recovered"] += 1
                counts[f"english_url_{match_method}"] += 1
            else:
                source_url_status = "not_recovered_from_available_book32_listing"
                counts["english_url_not_recovered"] += 1
        else:
            counts["chinese_url_not_retained"] += 1

        perceptual_hash = phash64(image_path)
        content_sha256 = sha256_file(image_path)
        phash_counts[perceptual_hash] += 1
        sha256_counts[content_sha256] += 1
        counts[f"records_{language}"] += 1

        rows.append(
            {
                "sample_id": sample_id,
                "source_collection": source_collection,
                "source_record_id": source_record_id,
                "source_url": source_url,
                "source_url_status": source_url_status,
                "phash_64": perceptual_hash,
                "sha256": content_sha256,
            }
        )
        if index % 500 == 0 or index == len(records):
            print(f"processed {index}/{len(records)}", flush=True)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    statistics = {
        "records": len(rows),
        "english_records": counts["records_english"],
        "chinese_records": counts["records_chinese"],
        "english_source_urls_recovered": counts["english_url_recovered"],
        "english_source_urls_exact_filename": counts["english_url_exact_filename"],
        "english_source_urls_unique_normalized_identifier": counts[
            "english_url_unique_normalized_identifier"
        ],
        "english_source_urls_not_recovered": counts["english_url_not_recovered"],
        "chinese_source_urls_not_retained": counts["chinese_url_not_retained"],
        "perceptual_hash_algorithm": (
            "64-bit pHash: grayscale 32x32, orthonormal 2D DCT-II, "
            "top-left 8x8 coefficients thresholded at their median"
        ),
        "perceptual_hashes_present": len(rows),
        "unique_perceptual_hashes": len(phash_counts),
        "perceptual_hash_duplicate_groups": sum(
            1 for count in phash_counts.values() if count > 1
        ),
        "sha256_hashes_present": len(rows),
        "unique_sha256_hashes": len(sha256_counts),
        "exact_duplicate_groups": sum(1 for count in sha256_counts.values() if count > 1),
        "original_image_pixels_included": False,
        "local_filesystem_paths_included": False,
    }
    args.output_statistics.parent.mkdir(parents=True, exist_ok=True)
    with args.output_statistics.open("w", encoding="utf-8") as stream:
        json.dump(statistics, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(statistics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
