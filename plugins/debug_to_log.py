import auto_derby
import logging

_LOGGER = logging.getLogger(__name__)


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        for handler in logging.root.handlers:
            if handler.__class__ is logging.StreamHandler:
                handler.setLevel(logging.INFO)
                _LOGGER.info("%s is set to WARNING level" % handler)
            if handler.__class__ is logging.handlers.RotatingFileHandler:
                handler.setLevel(logging.DEBUG)
                _LOGGER.info("%s is set to DEBUG level" % handler)


auto_derby.plugin.register(__name__, Plugin())
