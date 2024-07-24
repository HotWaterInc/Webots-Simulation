from typing import Dict, TypedDict, Callable, List, Union
from enum import Enum
from communication.communication_interface import JsonDataAction, action_types, \
    ActionTypeTeleportAbsolute, ActionTypeTeleportRelative, ActionTypeRotateAbsolute, ActionTypeRotateRelative, \
    ActionTypeSampleDistance, ActionTypeContRotateAbsolute, ActionTypeContForward, ActionTypeContW, ActionTypeContA, \
    ActionTypeContS, ActionTypeContD, ActionTypeSampleImage, ActionTypeSampleImageInference


class ActionController:
    __instance = None

    action_teleport_relative: Callable[[float, float], None] = None
    action_teleport_absolute: Callable[[float, float], None] = None
    action_rotate_absolute: Callable[[float], None] = None
    action_rotate_relative: Callable[[float], None] = None

    action_sample_distance: Callable[[], None] = None
    action_sample_image: Callable[[], None] = None
    action_sample_image_inference: Callable[[], None] = None

    action_continous_rotate_absolute: Callable[[float], None] = None
    action_continous_forward: Callable[[float], None] = None

    action_W: Callable[[], None] = None
    action_A: Callable[[], None] = None
    action_S: Callable[[], None] = None
    action_D: Callable[[], None] = None

    @staticmethod
    def get_instance():
        if ActionController.__instance is None:
            ActionController()
        return ActionController.__instance

    def __init__(self):
        if ActionController.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ActionController.__instance = self


def detach_action(json_data: JsonDataAction) -> None:
    # print(json_data)

    # if json_data.get("action_type") is None:
    #     raise Exception("action_type is required in json_data")
    # if json_data["action_type"] not in action_types:
    #     raise Exception(f"action_type {json_data['action_type']} is not a valid action type")

    action_controller: ActionController = ActionController.get_instance()

    if json_data["action_type"] == ActionTypeTeleportAbsolute:
        action_controller.action_teleport_absolute(json_data["x"], json_data["y"])
    elif json_data["action_type"] == ActionTypeTeleportRelative:
        action_controller.action_teleport_relative(json_data["dx"], json_data["dy"])
    elif json_data["action_type"] == ActionTypeRotateAbsolute:
        action_controller.action_rotate_absolute(json_data["angle"])
    elif json_data["action_type"] == ActionTypeRotateRelative:
        action_controller.action_rotate_relative(json_data["dangle"])
    elif json_data["action_type"] == ActionTypeSampleDistance:
        action_controller.action_sample_distance()
    elif json_data["action_type"] == ActionTypeSampleImage:
        action_controller.action_sample_image()
    elif json_data["action_type"] == ActionTypeSampleImageInference:
        action_controller.action_sample_image_inference()

    elif json_data["action_type"] == ActionTypeContRotateAbsolute:
        action_controller.action_continous_rotate_absolute(json_data["angle"])
    elif json_data["action_type"] == ActionTypeContForward:
        action_controller.action_continous_forward(json_data["distance"])

    elif json_data["action_type"] == ActionTypeContW:
        action_controller.action_W()
    elif json_data["action_type"] == ActionTypeContA:
        action_controller.action_A()
    elif json_data["action_type"] == ActionTypeContS:
        action_controller.action_S()
    elif json_data["action_type"] == ActionTypeContD:
        action_controller.action_D()
    else:
        raise Exception(f"action_type {json_data['action_type']} is not a valid action type")
