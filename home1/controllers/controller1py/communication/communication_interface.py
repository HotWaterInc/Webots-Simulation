from time import sleep as Sleep
import threading

from typing import Callable, Dict, TypedDict, Union, List


class CommunicationInterface:
    __instance = None

    send_data = None
    receive_data = None

    start_server = None
    server_started = False

    send_data_queue = []

    @staticmethod
    def get_instance():
        if CommunicationInterface.__instance is None:
            CommunicationInterface()
        return CommunicationInterface.__instance

    def __init__(self):
        if CommunicationInterface.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            CommunicationInterface.__instance = self


class TeleportAbsoluteAction(TypedDict):
    action_type: str
    x: float
    y: float


class TeleportRelativeAction(TypedDict):
    action_type: str
    dx: float
    dy: float


class RotateAbsoluteAction(TypedDict):
    action_type: str
    angle: float


class RotateRelativeAction(TypedDict):
    action_type: str
    dangle: float


class SampleAction(TypedDict):
    action_type: str
    pass


ActionTypeTeleportAbsolute = "teleport_absolute"
ActionTypeTeleportRelative = "teleport_relative"
ActionTypeRotateAbsolute = "rotate_absolute"
ActionTypeRotateRelative = "rotate_relative"
ActionTypeSample = "sample"

action_types: List[str] = [
    ActionTypeTeleportAbsolute, ActionTypeTeleportRelative, ActionTypeRotateAbsolute, ActionTypeRotateRelative,
    ActionTypeSample
]

JsonDataAction = Union[
    TeleportAbsoluteAction, TeleportRelativeAction, RotateAbsoluteAction, RotateRelativeAction, SampleAction]


def send_data(json_data: Dict) -> None:
    # abstract send_data function easy to use
    communication = CommunicationInterface.get_instance()
    if communication.server_started:
        communication.send_data(json_data)
    else:
        # if you call send_data before the server thread started, queue the data
        communication.send_data_queue.append(json_data)


def send_pending_data():
    communication = CommunicationInterface.get_instance()
    for data in communication.send_data_queue:
        send_data(data)


def receive_data(data: JsonDataAction):
    communication: CommunicationInterface = CommunicationInterface.get_instance()

    if data.get("action_type") is None:
        raise Exception("action_type is required in json_data")
    if data["action_type"] not in action_types:
        raise Exception(f"action_type {data['action_type']} is not a valid action type")

    communication.receive_data(data)


def set_server_started():
    communication = CommunicationInterface.get_instance()
    communication.server_started = True

    # Use a thread because this callback already runs in the thread that started the server ( since the callback is called by the server )
    # and we don't want to block the server, or use asyncio.run again in the callback since it does not work
    thread = threading.Thread(target=send_pending_data)
    thread.start()


def start_server():
    communication = CommunicationInterface.get_instance()
    if communication.start_server is not None:
        communication.start_server(set_server_started)
