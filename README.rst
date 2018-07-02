promesque
=========

*promesque* is a configurable Prometheus exporter for results of Elasticsearch queries.

Installation
------------

::

    pip install -e https://github.com/croesnick/promesque

Usage
-----

::

    promesque path/to/some/config.yml --log-level info

Refer to `exporter_es.yml` as an example for such a config.
The supported fields are explained below.


Configuration File
------------------

Configuration file is in a yaml format with single configuration scope (`metrics`).

Each item in `metrics` scope define a metric and must have following attributes:

- `metric_desc`: description of a metric (what it does)
- `metric_value`: reference to value in Elasticsearch response (json data)
- `metric_labels`: inner scope with `metric_name: reference` for each metric:
    - `metric_name`: name of label exposed by exporter
    - `reference`: reference to value in Elasticsearch response (json data)
- `es_url`: url to Elasticsearch cluster (include index)
- `es_query`: query in json format; must
    - _either_ be inclosed in single quotes (e.g. `'{ "query": {...} }'`)
    - _or_ written in [YAML block notation](http://yaml.org/spec/1.2/spec.html#|%20literal%20style//) with proper indentation, e.g.,

        ::

            es_query: |
              {
                "query": {
                  ...
                }
              }
