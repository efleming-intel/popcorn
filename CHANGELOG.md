# Changelog

Any notable change to this project will be documented in this file.

## Unreleased

- filter out processes that lack a duration

## [v0.0.3 Release (13-02-2024)](https://github.com/efleming-intel/popcorn/tree/v0.0.3)

- updated README.md
- added coveralls.io support
- rehauled console output for a cleaner look
- replaced json usage with ijson for more stable json file reading and allow reading of large json files

## [v0.0.2 Release (27-10-2023)](https://github.com/efleming-intel/popcorn/tree/v0.0.2)

- print display item count in console output
- folder input support (e.g. popcorn -f dirname)

## [v0.0.1 Release (23-10-2023)](https://github.com/efleming-intel/popcorn/tree/v0.0.1)

- hotspots and kernel differences analyzers
- input format support: level zero trace log (.json)
- output format support: console, xlsx, md, csv
- console supports three levels of verbosity
- filter trace events by category
