## About

This exporter intented to expose metrics based on Elasticsearch queries.
This exporter never run in production, so use it on your own risk :-)

## Requirements

Any modern Linux distro (Arch, Ubuntu, CentOS, Debian).

Following `python` libraries are required: `pyyaml`, `requests`, `prometheus_client`.

## Configuration File

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

        ```
        es_query: |
          {
            "query": {
              ...
            }
          }
        ```

Refer to `exporter_es.yml` as an example.

## Installation and running

```
virtualenv .pyenv
. .pyenv/bin/activate
pip install pyyaml requests prometheus_client
python exporter_es.py --conf exporter_es.yml --log-level INFO --log-file /tmp/exporter_es.log
```
