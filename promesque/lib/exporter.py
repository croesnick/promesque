import json

import requests
from jsonpath_ng import jsonpath, parse
from prometheus_client import Gauge


class ESGaugeMetric(object):
    def __init__(self, name, description, labels, data_path, value_path, url, query, value_converter=None, logger=None):
        '''
        name            -- name of metric (e.g., node_network_status)
        description     -- description of metric
        labels          -- indexes (tuple of strings) in metric_data taken as labels
        data_path       -- jsonpath to buckets of data to build metrics from
        value_path      -- jsonpath to value of the metric, located inside data referred to by `data_path`
        value_converter -- sometime value may came in mixed format like - 5s, 3GB.
                           we need to convert this value to numeric.
                           pass a function reference to this converter, can be lambda as well.
        url             -- elasticsearch url to index or GET query
        query           -- elasticsearch query data for POST request
        logger          -- instance of logging.Logger class
        '''
        self.gauge = Gauge(name, description, list(labels))
        self.name = name
        self.labels = labels
        self.data_path = data_path
        self.value_path = value_path
        self.value_converter = value_converter
        self.url = url
        self.query = query
        self.logger = logger

    @classmethod
    def es_query(cls, url, data):
        '''
        query Elasticsearch cluster and return raw requests.Response object
        url     -- url to elastic search e.g. - http://localhost:9200/bank/_search
        data    -- query in json format - more info reffer to Elasticsearch documentation
        return  -- raw requests.Response object
        '''
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(url, headers=headers, data=data)
        return resp

    def metrics(self, metric_data):
        '''
        populate labels and value with data
        metric_data -- dict object
        return      -- labels - list of dicts with label=value, value
        '''
        value_jsonpath = parse(self.value_path)

        data_jsonpath = parse(self.data_path)
        data = [item.value for item in data_jsonpath.find(metric_data)]

        for item in data:
            value_matches = value_jsonpath.find(item)
            if len(value_matches) != 1:
                self.logger.error('Expected exactly one metric value at value path={0}, got {1}'.format(
                    self.value_path,
                    len(value_matches)))
                raise ValueError

            value = value_matches[0].value
            if self.value_converter:
                value = self.value_converter(value)

            labels = {}
            for name, path in self.labels.items():
                label_jsonpath = parse(path)
                label_matches = label_jsonpath.find(item)
                if len(label_matches) != 1:
                    self.logger.error('Expected exactly one label value at path={0}, got {1}'.format(
                        path,
                        len(label_matches)))
                    raise ValueError

                labels[name] = label_matches[0].value

            yield labels, value

    def print_metric(self, metric_labels, metric_value):
        '''
        build and print metric
        metric_labels -- labels to print
        metric_value  -- value to print
        '''
        if metric_labels:
            label_value = []
            for label, value in metric_labels.items():
                label_value.append('{l}="{v}"'.format(l=label, v=value))
            # show labels in a log
            text = '{n}{{{lv}}} {v}'.format(n=self.name, lv=', '.join(label_value), v=metric_value)
        else:
            # there are no labels to show
            text = '{n} {v}'.format(n=self.name, v=metric_value)
        if self.logger:
            self.logger.info(text)
        else:
            print('[INFO]: {t}'.format(t=text))
        
    def update(self, print_metric=False):
        '''
        query ES and update metric with newer value
        print_metric    -- print metric to stdout (good for dev stage)
        '''
        resp = self.es_query(self.url, data=self.query)
        data = json.loads(resp.text)
        for labels, value in self.metrics(data):
            if print_metric:
                self.print_metric(labels, value)
            if self.labels:
                self.gauge.labels(**labels).set(value)
            else:
                self.gauge.set(value)
