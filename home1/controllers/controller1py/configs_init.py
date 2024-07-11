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
    # communication.send_data = sync_send
    communication.receive_data = detach_action


def configs_operation_mode():
    config = OperationModeInterface.get_instance()
    config.operation_mode = OperationMode.RECEIVE_COMMANDS


def config_actions(action_teleport_absolute: Callable[[float, float], any],
                   action_teleport_relative: Callable[[float, float], any],
                   action_rotate_absolute: Callable[[float], any],
                   action_rotate_relative: Callable[[float], any],
                   action_sample: Callable[[], any]):
    actions: ActionController = ActionController.get_instance()
    actions.action_teleport_absolute = action_teleport_absolute
    actions.action_teleport_relative = action_teleport_relative
    actions.action_rotate_absolute = action_rotate_absolute
    actions.action_rotate_relative = action_rotate_relative
    actions.action_sample = action_sample


def configs():
    # used to configure various parameters of the project such as communication, purpose,
    # This is the dirty hardcoded entry point for the project with all the concrete settings

    configs_communication()
    configs_operation_mode()
