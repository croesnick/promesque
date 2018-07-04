promesque
=========

*promesque* is a configurable Prometheus exporter for results of Elasticsearch queries.

Installation
------------

::

    pip3 install promesque

Usage
-----

::

    promesque path/to/some/config.yml --log-level info

Refer to ``exporter_es.yml`` as an example for such a config.
The supported fields are explained below.


Configuration File
------------------

Configuration file is in a yaml format with single configuration scope (``metrics``).

Each item in ``metrics`` scope define a metric and must have following attributes:

- ``description``: description of a metric (what it does)
- ``data_path``: jsonpath to data buckets in Elasticsearch response to build metrics from (default: ``$``)
- ``value_path``: jsonpath to metric value within data bucket
- ``labels``: inner scope with ``name: reference`` for each metric:
    - ``name``: name of label exposed by exporter
    - ``reference``: jsonpath to label value within data bucket
- ``url``: url to Elasticsearch cluster (include index)
- ``query``: query in json format; must
    - *either* be inclosed in single quotes (e.g. ``'{ "query": {...} }'``)
    - *or* written in `YAML block notation <http://yaml.org/spec/1.2/spec.html#|%20literal%20style//>`_
      with proper indentation, e.g.,

      ::

        es_query: |
          {
            "query": {
              ...
            }
          }