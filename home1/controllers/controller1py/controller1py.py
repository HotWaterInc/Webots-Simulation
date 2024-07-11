# ignore errors in this file
from controller import Supervisor
from time import sleep as Sleep
import threading
from communication.communication_interface import send_data
from configs_init import configs, config_actions
from robot_params.robot_params import RobotParams
from robot_params.operations_interface import OperationMode, operation_mode
from communication.communication_interface import start_server
from typing import Dict

robot = Supervisor()
RobotParams.get_instance().set_robot(robot)
RobotParams.get_instance().set_timestep(64)
RobotParams.get_instance().set_max_speed(6.28)
RobotParams.get_instance().set_start_time(0.0)

start_time = robot.getTime()
distance_sensors = []

timestep = RobotParams.get_instance().get_timestep()


def sensors_setup():
    supervisor = robot

    for i in range(robot.getNumberOfDevices()):
        device = robot.getDeviceByIndex(i)
        if 'distance sensor' in device.getName():
            # Enable the distance sensor
            device.enable(timestep)
            distance_sensors.append(device)

            sensor_node = supervisor.getFromDef(device.getName())

    names = [sensor.getName() for sensor in distance_sensors]


def main_loop():
    global start_time, phase, left_speed, right_speed
    front_left = robot.getDevice('W_LEFT')
    front_right = robot.getDevice('W_RIGHT')

    front_left.setPosition(float('inf'))
    front_left.setVelocity(0.0)

    front_right.setPosition(float('inf'))
    front_right.setVelocity(0.0)

    max_speed = RobotParams.get_instance().get_max_speed()
    timestep = RobotParams.get_instance().get_timestep()

    left_speed = max_speed
    right_speed = max_speed

    robot_node = robot.getFromDef("Robot")

    global set_coords_signal_bool, set_coords_signal_json
    global set_rotation_signal_bool, set_rotation_signal_json
    global set_sample_signal_bool

    while robot.step(timestep) != -1:
        if set_coords_signal_bool:
            x = set_coords_signal_json["x"]
            y = set_coords_signal_json["y"]
            set_robot_coords(x, y)
            set_coords_signal_bool = False

        if set_rotation_signal_bool:
            angle = set_rotation_signal_json["angle"]
            robot_node = robot.getFromDef("Robot")
            rotation_field = robot_node.getField("rotation")
            rotation_field.setSFRotation([0, 1, 0, angle])
            set_rotation_signal_bool = False

        if set_sample_signal_bool:
            data = collect_current_data()
            send_data(data)
            set_sample_signal_bool = False


set_coords_signal_bool = False
set_coords_signal_json = {
    "x": 0,
    "y": 0
}

set_rotation_signal_bool = False
set_rotation_signal_json = {
    "angle": 0
}

set_sample_signal_bool = False


def get_robot_coords():
    position = robot.getFromDef("Robot").getPosition()
    x = position[0]
    y = position[1]
    return x, y


def set_coords_signal(x, y):
    print("Setting coordinates", x, y)
    global set_coords_signal_bool, set_coords_signal_json
    set_coords_signal_json["x"] = x
    set_coords_signal_json["y"] = y
    set_coords_signal_bool = True


def set_robot_coords(x, y):
    robot_node = robot.getFromDef("Robot")
    translation_field = robot_node.getField("translation")
    translation_field.setSFVec3f([x, y, 0.05])
    robot.step(timestep)


def collect_current_data():
    sensor_data = []
    for sensor in distance_sensors:
        sensor_data.append(round(sensor.getValue(), 5))

    position = robot.getFromDef("Robot").getPosition()
    x = position[0]
    y = position[1]

    rotation = robot.getFromDef("Robot").getOrientation()
    angle = rotation[3]

    data = {
        "data": sensor_data,
        "params": {
            "x": x,
            "y": y,
            "angle": angle
        }
    }

    return data


def detach_robot_sample():
    print("called sampling")
    # json_data = collect_current_data()
    # send_data(json_data)
    global set_sample_signal_bool
    set_sample_signal_bool = True
    print("ended calling sampling")


def detach_robot_teleport_absolute(x: float, y: float):
    set_coords_signal(x, y)


def detach_robot_teleport_relative(dx: float, dy: float):
    print("relative start")
    x, y = get_robot_coords()
    set_coords_signal(x + dx, y + dy)
    print("relative end")


def detach_robot_rotate_absolute(angle: float):
    send_data({"action_type": "rotate_absolute", "angle": angle})


def detach_robot_rotate_relative(dangle: float):
    send_data({"action_type": "rotate_relative", "dangle": dangle})


if __name__ == '__main__':
    configs()
    config_actions(detach_robot_teleport_absolute, detach_robot_teleport_relative, detach_robot_rotate_absolute,
                   detach_robot_rotate_relative, detach_robot_sample)

    # external communication mechanism
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # simulation loop
    sensors_setup()
    main_loop()
