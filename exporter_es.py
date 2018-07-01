import os
import sys
import json
import time
import logging
import optparse
import requests
import yaml
from prometheus_client import start_http_server, Gauge

class ExporterError(Exception):
    pass

class ExporterLogger(logging.Logger):
    def __init__(self, name, path=None, level='ERROR', fmt='%(asctime)s [%(levelname)-5.5s]:  %(message)s'):
        try:
            # resolve textual level to numerical 
            level = getattr(logging, level)
        except Exception:
            raise ExporterError('wrong logging level {l}'.format(l=level))
        super(ExporterLogger, self).__init__(name, level)
        formatter = logging.Formatter(fmt)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        self.addHandler(stream_handler)
        if path:
            file_handler = logging.FileHandler(path)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.addHandler(file_handler)

class ESGaugeMetric(object):
    def __init__(self, name, desc, labels, value, value_converter, url, query, logger=None):
        '''
        name            -- metric name (e.g. node_network_status)
        desc            -- metric description
        labels          -- indexes (tuple of strings) in metric_data taken as labels
        value           -- index in metric_data (dict) taken as value for metric
        value_converter -- sometime value may came in mixed format like - 5s, 3GB.
                           we need to convert this value to numeric.
                           pass a function reference to this converter, can be lambda as well.
        url             -- elasticsearch url to index or GET query
        query           -- elasticsearch query data for POST request
        logger          -- instance of logging.Logger class
        '''
        self.gauge = Gauge(name, desc, list(labels))
        self.name = name
        self.labels = labels
        self.value = value
        self.value_converter = value_converter
        self.url = url
        self.query = query
        self.logger = logger

    def path_converter(self, path):
        '''
        convert path from indexA.indexB to ['indexA']['indexB']
        path    -- path in dot notaion
        return  -- path in bracket notaion
        '''
        elems = []
        for elem in path.split('.'):
            bracket = "['{0}']".format(elem)
            elems.append(bracket)
        return ''.join(elems)

    def es_query(self, url, data):
        '''
        query Elasticsearch cluster and return raw requests.Response object
        url     -- url to elastic search e.g. - http://localhost:9200/bank/_search
        data    -- query in json format - more info reffer to Elasticsearch documentation
        return  -- raw requests.Response object
        '''
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(url, headers=headers, data=data)
        return resp

    def populate(self, metric_data):
        '''
        populate labels and value with data
        metric_data -- dict object
        return      -- metric_labels - dict with label=value, metric_value - converted value
        '''
        try:
            converter = getattr(self, self.value_converter)
        except Exception:
            converter = self.value_converter
        value_path = self.path_converter(self.value)
        value_var = 'metric_data{0}'.format(value_path)
        metric_value = converter(eval(value_var))
        metric_labels = {}
        for label_name, label_path in self.labels.items():
            label_path = self.path_converter(label_path)
            label_var = 'metric_data{0}'.format(label_path)
            metric_labels[label_name] = eval(label_var)
        return metric_labels, metric_value

    def print_metric(self, metric_labels, metric_value):
        '''
        build and print metric
        metric_labels -- labels to print
        metric_value  -- value to print
        '''
        if metric_labels:
            label_value = []
            for label, value in metric_labels.items():
                label_value.append('{l}={v}'.format(l=label, v=value))
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
        metric_data = json.loads(resp.text)
        metric_labels, metric_value = self.populate(metric_data)
        if print_metric:
            self.print_metric(metric_labels, metric_value)
        if self.labels:
            self.gauge.labels(**metric_labels).set(metric_value)
        else:
            self.gauge.set(metric_value)

if __name__ == '__main__':
    usage = '%prog --conf [--port --interval, --log-file, --log-level]'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-p', '--port', type='int', help='port to bind prometheus exporter', default=9100)
    parser.add_option('-i', '--interval', type='int', help='interval to probe nodes and update metrics', default=60)
    parser.add_option('-c', '--conf', type='str', help='path to a conf file')
    parser.add_option('-l', '--log-file', type='str', help='path to a log file', default=None)
    parser.add_option('-L', '--log-level', type='str', help='levels available: DEBUG,INFO,WARNING,ERROR,CRITICAL', default='ERROR')
    opts, args = parser.parse_args()
    logger = ExporterLogger('exporter_es', path=opts.log_file, level=opts.log_level)
    if not opts.conf:
        raise ExporterError('configuration file is a required argument')
    if not os.path.isfile(opts.conf):
        raise ExporterError('file {c} do not exists'.format(c=opts.conf))
    with open(opts.conf, 'r') as f:
        try:
            conf = yaml.load(f)
        except Exception as ex:
            print('[ERROR]: failed to parse configuration file {0} ...'.format(opts.conf))
            sys.exit(1)
    # store all metrics in a list
    metrics = []
    # get metric params from config
    conf_metrics = conf['metrics']
    for metric_name, metric_params in conf_metrics.items():
        metric_desc = metric_params['metric_desc']
        metric_value = metric_params['metric_value']
        es_url = metric_params['es_url']
        es_query = metric_params['es_query']
        # metric_labels is not required config param, hence need to create it's default
        metric_labels = {}
        if 'metric_labels' in metric_params:
            metric_labels = metric_params['metric_labels']
        # create and store metric
        metric = ESGaugeMetric(metric_name, metric_desc, metric_labels, metric_value, int, es_url, es_query, logger=logger)
        metrics.append(metric)
    start_http_server(opts.port)
    while True:
        for metric in metrics:
            try:
                metric.update(print_metric=True)
            except Exception as ex:
                logger.error(ex)
        time.sleep(opts.interval)
