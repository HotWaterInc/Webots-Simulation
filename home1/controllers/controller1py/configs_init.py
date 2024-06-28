from communication.communication_interface import CommunicationInterface
from communication.websockets_client import start_websockets, send_data
from robot_params import RobotParams, OperationMode, OperationModeInterface
from communication import CommunicationInterface
from action_controller import detach_action
from action_controller import ActionController


def configs_communication():
    # abstracts away the communication details
    communication = CommunicationInterface.get_instance()

    communication.start_server = start_websockets
    communication.send_data = send_data
    communication.receive_data = detach_action


def configs_operation_mode():
    configs = OperationModeInterface.get_instance()
    configs.operation_mode = OperationMode.RECEIVE_COMMANDS


def config_actions(action1, action2, action3):
    actions = ActionController.get_instance()
    actions.action1 = action1
    actions.action2 = action2
    actions.action3 = action3


def configs():
    # used to configure various parameters of the project such as communication, purpose,
    # This is the dirty hardcoded entry point for the project with all the concrete settings

    configs_communication()
    configs_operation_mode()
