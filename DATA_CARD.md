# Dataset Card for BookLayout-Bi

> Draft for internal verification. Fields marked `TODO` must be resolved before public release.

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

## Sources

- English subset: sampled from the publicly available [Book Dataset Task 2 (Book32)](https://github.com/uchidalab/book-dataset/tree/master/Task2).
- Chinese subset: collected from publicly accessible official websites of eight Chinese publishers.
- TODO: recover and verify per-record source information where available.
- TODO: document limitations for records whose original URL can no longer be recovered.

## Experimental split

- Held-out test set: 194 manually annotated records.
- Stage 1 pool after excluding the held-out set: 9,967 records, split into 8,971 training and 996 validation records.
- Stage 2 manual pool after excluding the held-out set: 1,746 records, split into 1,572 training and 174 validation records.
- Split seed: 42.
- Training random seeds reported for the final model: 0, 1, 2, 3, and 4.

## Copyright and access

The original book-cover artwork is not redistributed because it may remain protected by third-party copyright. Users must obtain source images independently and comply with the terms of the corresponding source websites.

## Known preparation tasks

- TODO: generate stable public sample identifiers.
- TODO: remove local image paths from all released records.
- TODO: generate and verify all fixed split files.
- TODO: recover available source URLs without inventing missing provenance.
- TODO: compute perceptual hashes locally if they are retained in the availability statement.
- TODO: select a license for the author-created annotations and metadata.
