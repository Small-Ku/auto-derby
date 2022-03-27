import auto_derby
from auto_derby import window


import logging

_LOGGER = logging.getLogger(__name__)


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        _LOGGER.info(logging.root.handlers)
        for handler in logging.root.handlers:
            if handler.__class__ is logging.StreamHandler:
                handler.setLevel(logging.INFO)
                _LOGGER.info("%s is set to WARNING level" % handler)
            if handler.__class__ is logging.handlers.RotatingFileHandler:
                handler.setLevel(logging.DEBUG)
                _LOGGER.info("%s is set to DEBUG level" % handler)
        _LOGGER.info(logging.root.handlers)


auto_derby.plugin.register(__name__, Plugin())
