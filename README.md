# BookLayout-Bi

> Preparation copy: this repository is not yet ready for public release.

BookLayout-Bi is a bilingual book-cover layout dataset used to evaluate LGC-Net. The final experimental set contains 10,161 Chinese and English cover-layout records. Each released record will contain structured layout annotations and cover-level attributes, but no original cover-image pixels.

## Planned public contents

- normalized bounding-box annotations for nine functional element categories;
- subject and language labels;
- fixed training, validation, and held-out test splits;
- annotation schema and dataset statistics;
- source and cleaning documentation that can be legally redistributed;
- an audit list for records excluded from the reported experiments.

## Copyright boundary

The underlying cover artwork remains subject to third-party copyright. Original cover images will not be redistributed through this repository. This repository will release only author-created structured annotations, identifiers, split files, and legally distributable provenance information.

## Current preparation status

The source corpus contains 10,171 cleaned records. Ten records without detectable layout elements are excluded, leaving 10,161 records for the reported experiments. The public package will not be released until its record counts, split membership, provenance fields, and privacy checks have been verified.

Run `python tools/validate_release.py` from the repository root to verify record counts, split membership, bounding-box ranges, and the absence of image pixels.

## License

The license will be selected after author and institutional confirmation. No license is granted by this preparation copy.
