from communication.communication_interface import CommunicationInterface
from communication.websockets_client import start_websockets, send_data
from robot_params import RobotParams, OperationMode, OperationModeInterface
from communication import CommunicationInterface
from action_controller import detach_action
from action_controller import ActionController
from typing import Callable, Dict


def configs_communication():
    # abstracts away the communication details
    communication = CommunicationInterface.get_instance()

    communication.start_server = start_websockets
    communication.send_data = send_data
    communication.receive_data = detach_action


def configs_operation_mode():
    config = OperationModeInterface.get_instance()
    config.operation_mode = OperationMode.RECEIVE_COMMANDS


def config_actions(action_request_data: Callable[[], Dict], action_go_to: Callable[[Dict], Dict],
                   action_teleport_to: Callable[[Dict], Dict]):
    actions: ActionController = ActionController.get_instance()
    actions.action_request_data = action_request_data
    actions.action_go_to = action_go_to
    actions.action_teleport_to = action_teleport_to


def configs():
    # used to configure various parameters of the project such as communication, purpose,
    # This is the dirty hardcoded entry point for the project with all the concrete settings

    configs_communication()
    configs_operation_mode()
