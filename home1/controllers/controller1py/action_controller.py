from typing import Dict, TypedDict, Callable
from enum import Enum

class ActionController:
    __instance = None

    action_go_to: Callable[[Dict], Dict]
    action_teleport_to: Callable[[Dict], Dict]
    action_request_data: Callable[[], Dict]

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

class ActionTypes(Enum):
    TELEPORT_TO = "TELEPORT_TO"
    GO_TO = "GO_TO"
    REQUEST_DATA = "REQUEST_DATA"

class ActionFormat(TypedDict):
    action_type: str
    args: Dict[str, any]

def detach_action(json_data: Dict) -> None:
    actions = ActionController.get_instance()
    print(json_data)
    return None
    action_type: ActionTypes = json_data["action_type"]
    print("in detach action")
    print(json_data)
    if action_type not in ActionTypes:
        raise Exception("Invalid action type")

    if action_type == ActionTypes.TELEPORT_TO:
        actions.action_go_to(json_data["args"])

    elif action_type == ActionTypes.GO_TO:
        actions.action_teleport_to(json_data["args"])

    elif action_type == ActionTypes.REQUEST_DATA:
        actions.action_request_data(json_data["args"])
