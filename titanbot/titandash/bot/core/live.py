from django.core.cache import cache

from titandash.bot.core.utilities import make_logger
from titandash.bot.core.utilities import globals

from pathlib import Path

import inspect
import logging


__configuration_base__ = ("_configuration", "_logger", "_fields", "_cache_key")
___logger_base__ = ()


class LiveConfiguration:
    """
    Live configuration wrapper that allows changes to be made to the configuration
    while a bot session is running, this allows users to change settings and have them apply
    instantaneously to any running instances that are using the configuration.
    """
    def __init__(self, configuration):
        self._configuration = configuration
        self._fields = [f.name for f in configuration._meta.get_fields() if not f.name.startswith("_")]

    def _get_cache_state(self):
        """
        Retrieve the cached instance of our configuration here.

        The cached version of this remains forever, until our configuration
        has been removed from the cache, which takes place when a configuration
        is saved.
        """
        return cache.get_or_set(
            key=self._configuration.cache_key,
            default=self.__reload,
            timeout=None  # Never expire.
        )

    def __reload(self):
        """
        Reload the current configuration object, re-retrieving it from the database.
        """
        self._configuration.refresh_from_db()

        # Return configuration object once we've refreshed it
        # directly from the database.
        return self._configuration

    def __getattr__(self, item):
        """
        Custom attribute getter to retrieve values from our live configuration.
        """
        if item in __configuration_base__:
            return super(LiveConfiguration, self).__getattribute__(item)
        if item in self._fields:
            return getattr(self._get_cache_state(), item)

    def __setattr__(self, key, value):
        """
        Custom attribute setter to set values on our live configuration.
        """
        if key in __configuration_base__:
            super(LiveConfiguration, self).__setattr__(key, value)
        elif key in self._fields:
            setattr(self._configuration, key, value)


class UpStackedLogger:
    """
    Using a custom up stacked logger to retrieve the proper filename and line numbers when formatting records
    through our live logger wrapper utility.
    """
    def __init__(self, logger, n):
        self.logger = logger

        calling_frame = inspect.stack()[n + 1].frame
        trace = inspect.getframeinfo(calling_frame)

        class UpStackFilter(logging.Filter):
            def filter(self, record):
                record.lineno, record.pathname, record.filename, record.funcName = \
                    trace.lineno, trace.filename, Path(trace.filename).name, trace.function
                return True

        self.f = UpStackFilter()

    def __enter__(self):
        self.logger.addFilter(self.f)
        return self.logger

    def __exit__(self, *args, **kwargs):
        self.logger.removeFilter(self.f)


class LiveLogger:
    """
    Live logger wrapper that allows live changes made to the logging settings on a configuration
    to propagate up into our logger to ensure that logging enabling and logging levels are used in real time.
    """
    def __init__(self, instance, configuration):
        self.instance = instance
        self.configuration = configuration
        self.logger = make_logger(
            instance=instance,
            log_level=globals.logging_level(),
            log_file=None,
        )

    def log(self, level, message):
        """
        Generic logging method, wrapping the normal logger implementations numerous
        methods like "INFO, WARNING, ERROR" etc... We do additional checks on top
        of the base logger made during initialization.
        """
        # Ensure the logging level has been updated to the most up to date
        # global log level.
        self.logger.setLevel(level=globals.logging_level())

        # Send the actual log message through the logger backend.
        # Up stacked logger ensures we use the proper frame for log messages.
        with UpStackedLogger(logger=self.logger, n=2) as logger:
            getattr(logger, level.lower())(msg=message)

    def debug(self, message):
        """
        Attempt to send a debug log message.
        """
        self.log(level="DEBUG", message=message)

    def info(self, message):
        """
        Attempt to send an informational log message.
        """
        self.log(level="INFO", message=message)

    def warning(self, message):
        """
        Attempt to send a warning log message.
        """
        self.log(level="WARNING", message=message)

    def error(self, message):
        """
        Attempt to send an error log message.
        """
        self.log(level="ERROR", message=message)

    def exception(self, message):
        """
        Attempt to send an error message with exception information attached.
        """
        self.log(level="EXCEPTION", message=message)

    def critical(self, message):
        """
        Attempt to send a critical log message.
        """
        self.log(level="CRITICAL", message=message)
