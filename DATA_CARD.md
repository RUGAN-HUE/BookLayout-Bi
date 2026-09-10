# Dataset Card for BookLayout-Bi

> Preparation copy. Repository visibility must remain private until the authors approve public release.

## Dataset summary

- Raw collection size: approximately 27,000 Chinese and English book covers in total.
- Cleaned source records: 10,171.
- Records used in the reported experiments: 10,161.
- Excluded records: 10 records with no detectable layout elements.
- Languages: Chinese and English.
- Subject categories: Arts, Engineering, and Science.
- Functional element categories: nine.
- Annotation types: manual and automatic.

## Intended release

The release will contain structured layout annotations, cover-level labels, fixed experimental splits, schema documentation, and legally distributable provenance information. It will not contain original cover-image pixels.

The reported task predicts normalized element bounding boxes from element roles and optional cover-level conditions. It does not use cover-image pixels during model training or evaluation, so the structured package is sufficient to rerun the reported coordinate-generation pipeline.

## Sources

- English subset: sampled from the publicly available [Book Dataset Task 2 (Book32)](https://github.com/uchidalab/book-dataset/tree/master/Task2).
- Chinese subset: collected from publicly accessible official websites of eight Chinese publishers.
- Source URLs were recovered for 4,723 of the 5,083 English records from the retained Book32 listing. The remaining 360 English URLs could not be recovered reliably.
- Per-record source URLs for the 5,078 Chinese records were not retained during collection. Missing provenance is marked explicitly and is not reconstructed or invented.
- All 10,161 records include a 64-bit perceptual hash and a SHA-256 hash computed locally from the retained source image. These hashes support integrity and duplicate audits without redistributing image pixels.

## Experimental split

- Held-out test set: 194 manually annotated records.
- Stage 1 pool after excluding the held-out set: 9,967 records, split into 8,971 training and 996 validation records.
- Stage 2 manual pool after excluding the held-out set: 1,746 records, split into 1,572 training and 174 validation records.
- Split seed: 42.
- Split text files preserve the deterministic record order used by the released evaluation pipeline; byte-level digests are recorded in `statistics/split_manifest.json`.
- Training random seeds reported for the final model: 0, 1, 2, 3, and 4.

## Copyright and access

The original book-cover artwork is not redistributed because it may remain protected by third-party copyright. Users must obtain source images independently and comply with the terms of the corresponding source websites.

The author-created bounding-box annotations and metadata are separated from the third-party artwork and licensed under CC BY-NC 4.0 for noncommercial use. Author-created scripts under `tools/` are licensed separately under PolyForm Noncommercial 1.0.0. Neither license applies to the underlying cover artwork, publisher logos, or other third-party content.

## Quality and split limitations

- The dataset includes automatic weak annotations as well as manual annotations; `annotation_type` identifies the source of each record's labels.
- The dataset itself preserves all annotated elements. The reported LGC-Net configuration has a model-specific maximum sequence length of 15 and therefore retains the first 15 elements in stored record order for 24 longer Stage 1 records. No Stage 2 or held-out test record exceeds 15 elements. Baselines may use their own documented sequence limits.
- A post-hoc audit found 29 groups of byte-identical source files. None crosses into the held-out test split.
- A perceptual-hash audit followed by visual verification found two same-cover pairs crossing between the training and test partitions under different identifiers. The affected test records are 2 of 194. The fixed split is retained to preserve the exact reported protocol; details are in `statistics/duplicate_audit.json`.
- One additional equal-perceptual-hash train/test pair was visually inspected and determined to be different titles using the same series design, so it is not classified as a duplicate.
- Perceptual hashes are screening signals and may contain both false positives and false negatives; they are not a substitute for full provenance or human verification.

## Citation and reuse

- Reuse must follow the noncommercial and attribution conditions in `LICENSE` and `LICENSE_SCOPE.md`.
- Publications using BookLayout-Bi should cite the associated paper and the archived dataset release once its DOI is available.
