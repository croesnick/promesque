import logging
import sys
import time

import click
from prometheus_client import start_http_server
from ruamel import yaml

from promesque.lib.exporter import ESGaugeMetric
from promesque.lib.exporter_logger import ExporterLogger, LOG_LEVEL_MAP

logger = ExporterLogger('promesque')


@click.command()
@click.argument('config', type=click.Path(exists=True))
@click.option('--port', default=9100, help='Port to bind prometheus exporter')
@click.option('--interval', default=60, help='Interval to probe nodes and update metrics (in seconds)')
@click.option('--log-file', type=click.Path(writable=True), help='Path to log file to write')
@click.option('--log-level', type=click.Choice(LOG_LEVEL_MAP.keys()), default='error')
def cli(config, port, interval, log_file, log_level):
    logger.setLevel(ExporterLogger.level(log_level))
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logger.formatter)
        logger.addHandler(file_handler)

    with open(config, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except Exception as e:
            logger.error('Failed to parse configuration file {0}. Errors: {1}'.format(config, e))
            sys.exit(1)

    # store all metrics in a list
    metrics = []
    # get metric params from config
    conf_metrics = config['metrics']
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

    start_http_server(port)

    while True:
        for metric in metrics:
            try:
                metric.update(print_metric=True)
            except Exception as e:
                logger.error(e)
        time.sleep(interval)


if __name__ == '__main__':
    cli()
