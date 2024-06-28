import enum


class OperationMode(enum.Enum):
    RECEIVE_COMMANDS = 1
    SEND_DATA = 2


class OperationModeInterface:
    __instance = None
    operation_mode: OperationMode = None

    @staticmethod
    def get_instance():
        if OperationModeInterface.__instance is None:
            OperationModeInterface()
        return OperationModeInterface.__instance

    def __init__(self):
        if OperationModeInterface.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            OperationModeInterface.__instance = self


def operation_mode():
    configs = OperationModeInterface.get_instance()
    return configs.operation_mode
