import sys
import logging


class SimulatorLoggerWrapper:
    class _LoggerFactory:
        @staticmethod
        def fetch_logger_instance() -> logging.Logger:
            ret: logging.Logger = logging.getLogger('simulator')
            ret.setLevel(logging.DEBUG)

            handler: logging.StreamHandler = logging.StreamHandler(sys.stderr)
            handler.setLevel(logging.INFO)

            formatter: logging.Formatter = logging.Formatter(fmt='(%(asctime)s) %(levelname)s: %(message)s')
            handler.setFormatter(formatter)

            ret.addHandler(handler)

            # Other stuff can be done to initialize the logger here

            return ret

    __simulator_logger: logging.Logger = _LoggerFactory.fetch_logger_instance()

    @staticmethod
    def logger() -> logging.Logger:
        return SimulatorLoggerWrapper.__simulator_logger
