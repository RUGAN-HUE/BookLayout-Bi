# BookLayout-Bi

> Preparation copy: this repository is not yet ready for public release.

BookLayout-Bi is a bilingual book-cover layout dataset used to evaluate LGC-Net. The final experimental set contains 10,161 Chinese and English cover-layout records. Each record contains structured layout annotations and cover-level attributes, but no original cover-image pixels.

## Repository contents

- normalized bounding-box annotations for nine functional element categories;
- subject and language labels;
- fixed training, validation, and held-out test splits;
- annotation schema and dataset statistics;
- legally distributable provenance fields, including available source URLs,
  64-bit perceptual hashes, and SHA-256 hashes;
- an audit list for records excluded from the reported experiments.

## Copyright boundary

The underlying cover artwork remains subject to third-party copyright. Original cover images will not be redistributed through this repository. This repository will release only author-created structured annotations, identifiers, split files, and legally distributable provenance information.

## Current preparation status

The source corpus contains 10,171 cleaned records. Ten records without detectable layout elements are excluded, leaving 10,161 records for the reported experiments. The released annotations are self-contained for the coordinate-only layout generation and evaluation task; source images are not consumed by the reported LGC-Net pipeline.

Run `python tools/validate_release.py` from the repository root to verify record counts, split membership, bounding-box ranges, provenance integrity, and the absence of image pixels and local paths.

## Provenance coverage

- English records: 5,083, sampled from Book Dataset--Task 2 (Book32).
- English source URLs recovered from the retained Book32 listing: 4,723.
- English records whose original URL could not be recovered: 360.
- Chinese records: 5,078, collected from the official websites of eight Chinese publishers.
- Per-record Chinese source URLs were not retained during collection and are not reconstructed or invented here.
- Perceptual and SHA-256 hashes are provided for all 10,161 source images, but the source-image pixels are not redistributed.

## Split audit

The fixed split is the split used in the manuscript. The text files preserve both split membership and the deterministic record order consumed by the evaluation scripts. Byte-level SHA-256 digests are provided in `statistics/split_manifest.json`.

A post-hoc hash and visual audit found two test records whose source covers are visually duplicated in the non-test pool under different record identifiers. The original experimental split and reported results are retained for traceability. Details are provided in `statistics/duplicate_audit.json`; this limitation should be considered when interpreting the benchmark.

## License

The license will be selected after author and institutional confirmation. No license is granted by this preparation copy.
