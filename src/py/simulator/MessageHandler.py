class MessageHandler:
    class __MessageHandler:
        def emit_error(self, message: str) -> None:
            print('ERROR:', message)

        def emit_warning(self, message: str) -> None:
            print('Warning:', message)

        def emit_info(self, message: str) -> None:
            print('info:', message)

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
