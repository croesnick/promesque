## About

This exporter intented to expose metrics based on Elasticsearch queries. This exporter never run in production, so use it on your own risk :-)

## Requirements

Any modern Linux distro (Arch, Ubuntu, CentOS, Debian).
Following `python2.7` libraries are required: `pyyaml, requests, prometheus_client`

## Configuration File

Configuration file is in a yaml format with single configuration scope (`metrics`). Each item in `metrics` scope define a metric and must have following attributes:
    - metric_desc - description of a metric (what it does)
    - metric_value - reference to value in Elasticsearch response (json data)
    - metric_labels - inner scope with `metric_name: reference` for each metric:
        - metric_name - name of label exposed by exporter
        - reference - reference to value in Elasticsearch response (json data)
    - es_url - url to Elasticsearch cluster (include index)
    - es_query - query in json format - MUST be inclosed in single quotes - e.g. '{ "query": {...} }'

Reffer to `exporter_es.yml` as an example

## Installation and running

```
virtualenv2 .pyenv
. .pyenv/bin/activate
pip install pyyaml requests prometheus_client
python2 exporter_es.py --conf exporter_es.yml --log-level INFO --log-file /tmp/exporter_es.log
```
