# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.3] - 2018-10-26

### Added

- travis-ci configuration
- Explicit support for Python 3.5

### Fixed

- Added missing __init__.py

## [0.0.2] - 2018-07-04

### Changed

- Change default port from 9100 to 9349 to be a good OSS citizen and use a free port from the to-be-considered
  [Prometheus port range](https://github.com/prometheus/prometheus/wiki/Default-port-allocations)

## [0.0.1] - 2018-07-04

### Added

- Basic configurable exporter, gathering data from Elasticsearch and reformatting it in
  [Prometheus' exposition format](https://github.com/prometheus/docs/blob/master/content/docs/instrumenting/exposition_formats.md)

[Unreleased]: https://github.com/croesnick/promesque/compare/v0.0.2...HEAD
[0.0.2]: https://github.com/croesnick/promesque/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/croesnick/promesque/compare/v0.0.1
