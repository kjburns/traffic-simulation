import sys


class MessageHandler:
    class __MessageHandler:
        def __init__(self, output_stream=sys.stderr):
            self.__output_stream = output_stream

        def emit_error(self, message: str) -> None:
            self.__output_stream.write('ERROR: ' + message + '\n')

        def emit_warning(self, message: str) -> None:
            self.__output_stream.write('Warning: ' + message + '\n')

        def emit_info(self, message: str) -> None:
            self.__output_stream.write(('info: ' + message + '\n'))

    __instance: __MessageHandler = __MessageHandler()

    def __getattr__(self, item):
        return getattr(MessageHandler.__instance, item)

    @staticmethod
    def emit_error(message: str) -> None:
        MessageHandler.__instance.emit_error(message)

    @staticmethod
    def emit_warning(message: str) -> None:
        MessageHandler.__instance.emit_warning(message)

    @staticmethod
    def emit_info(message: str) -> None:
        MessageHandler.__instance.emit_info(message)
