# ignore errors in this file
from controller import Robot
from controller import Supervisor
from tcp_socket_send import start_client, send_data
from movement import Movement, TeleportType
from global_params import GlobalParams
from threading import Thread
from time import sleep as Sleep
import enum
from tcp_socket_receive import start_command_server, run_server_in_thread, set_callback
import asyncio
import threading


class OperationMode(enum.Enum):
    RECEIVE_COMMANDS = 1
    SEND_DATA = 2


operation_mode = OperationMode.RECEIVE_COMMANDS

robot = Supervisor()
GlobalParams.get_instance().set_robot(robot)
GlobalParams.get_instance().set_timestep(64)
GlobalParams.get_instance().set_max_speed(6.28)
GlobalParams.get_instance().set_start_time(0.0)

start_time = robot.getTime()
distance_sensors = []

timestep = GlobalParams.get_instance().get_timestep()
width = 4
height = 4
movement = Movement.get_instance()
movement.set_teleport_type(TeleportType.TELEPORT8x8, width, height)


def print_node_rotation(node_name):
    node = robot.getFromDef(node_name)
    print(node.getOrientation())


def print_node_position(node_name):
    node = robot.getFromDef(node_name)
    print(node.getPosition())


def sensors_setup():
    supervisor = robot

    for i in range(robot.getNumberOfDevices()):
        device = robot.getDeviceByIndex(i)
        if 'distance sensor' in device.getName():
            # Enable the distance sensor
            device.enable(timestep)
            distance_sensors.append(device)

            sensor_node = supervisor.getFromDef(device.getName())


def main_loop():
    global start_time, phase, left_speed, right_speed
    front_left = robot.getDevice('W_LEFT')
    front_right = robot.getDevice('W_RIGHT')

    front_left.setPosition(float('inf'))
    front_left.setVelocity(0.0)

    front_right.setPosition(float('inf'))
    front_right.setVelocity(0.0)

    max_speed = GlobalParams.get_instance().get_max_speed()
    timestep = GlobalParams.get_instance().get_timestep()

    left_speed = max_speed
    right_speed = max_speed

    robot_node = robot.getFromDef("Robot")
    translation_field = robot_node.getField("translation")
    finished = 0
    offset_x = -width / 2
    offset_y = 0

    while robot.step(timestep) != -1:
        if operation_mode == OperationMode.SEND_DATA:
            if finished == 1:
                print("SEND END")
                send_data("END")
                return 0

            if finished == 0:
                finished = teleport(translation_field, offset_x, offset_y)
                Sleep(0.2)
                print("sleepy time")
        else:
            pass


def set_coords(x, y):
    print("Setting coordinates", x, y)
    robot_node = robot.getFromDef("Robot")
    translation_field = robot_node.getField("translation")
    translation_field.setSFVec3f([x, y, 0.05])


def teleport(translation_field, offset_x=0.0, offset_y=0.0):
    movement = Movement.get_instance()

    result = movement.get_teleport_indices()
    if result is None:
        return 1

    i, j = result
    x_coord, y_coord = movement.get_teleport_coords(i, j)

    x_coord += offset_x
    y_coord += offset_y

    print(f"Teleporting to {x_coord}, {y_coord}")
    translation_field.setSFVec3f([x_coord, y_coord, 0.05])
    robot.step(timestep)

    collect_current_data(i, j)
    return 0


def collect_current_data(i_index, j_index):
    sensor_data = []
    for sensor in distance_sensors:
        sensor_data.append(round(sensor.getValue(), 5))

    name = "" + str(i_index) + "_" + str(j_index)
    position = robot.getFromDef("Robot").getPosition()
    x = position[0]
    y = position[1]
    print(f"Data collected: {i_index, j_index} at {x}, {y}")

    data = {
        "data": sensor_data,
        "name": name,
        "params": {
            "i": i_index,
            "j": j_index,
            "x": x,
            "y": y
        }
    }

    send_data(data)


if __name__ == '__main__':
    if operation_mode == OperationMode.RECEIVE_COMMANDS:
        server_thread = threading.Thread(target=run_server_in_thread, daemon=True)
        server_thread.start()
        set_callback(set_coords)
    else:
        start_client()
    sensors_setup()
    main_loop()
