import logging
import sys


LOG_LEVEL_MAP = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


class ExporterError(Exception):
    pass


class ExporterLogger(logging.Logger):
    def __init__(self, name, path=None, level='error', fmt='%(asctime)s [%(levelname)-5.5s]:  %(message)s'):
        self._path = path
        self._level = self.level(level)

        super(ExporterLogger, self).__init__(name, self._level)
        self._formatter = logging.Formatter(fmt)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(self._formatter)
        self.addHandler(stream_handler)

    @classmethod
    def level(cls, level):
        return LOG_LEVEL_MAP[level.lower()]

    @property
    def formatter(self):
        return self._formatter
