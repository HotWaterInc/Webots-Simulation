# ignore errors in this file
from controller import Supervisor
from controller import Camera
from time import sleep as Sleep
import threading
from communication.communication_interface import send_data
from configs_init import configs, config_actions
from robot_params.robot_params import RobotParams
from robot_params.operations_interface import OperationMode, operation_mode
from communication.communication_interface import start_server
from typing import Dict
import math

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


def rotate_left():
    global left_speed, right_speed
    left_speed = -RobotParams.get_instance().get_max_speed()
    right_speed = RobotParams.get_instance().get_max_speed()


def rotate_right():
    global left_speed, right_speed
    left_speed = RobotParams.get_instance().get_max_speed()
    right_speed = -RobotParams.get_instance().get_max_speed()


def move_forward():
    global left_speed, right_speed
    left_speed = -RobotParams.get_instance().get_max_speed()
    right_speed = -RobotParams.get_instance().get_max_speed()


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
    global set_rotate_continous_signal_bool, set_rotate_continous_signal_json
    global set_forward_continous_signal_bool, set_forward_continous_signal_json

    starting_positionxy = [0, 0]
    init_forward = 0

    rotations = 0
    prev_angle = 0

    camera = robot.getDevice("CAM_NAME")
    camera.enable(timestep)

    saved = 0

    while robot.step(timestep) != -1:
        if saved == 0:
            result = camera.saveImage('my_camera_image.jpg', 100)
            print(result, "image saved")
            saved = 1

        if set_coords_signal_bool:
            x = set_coords_signal_json["x"]
            y = set_coords_signal_json["y"]
            set_robot_coords(x, y)
            set_coords_signal_bool = False
            send_ok_status()

        if set_rotation_signal_bool:
            angle = set_rotation_signal_json["angle"]
            robot_node = robot.getFromDef("Robot")
            rotation_field = robot_node.getField("rotation")
            rotation_field.setSFRotation([0, 0, 1, angle])
            set_rotation_signal_bool = False
            send_ok_status()

        if set_sample_signal_bool:
            data = collect_current_data(robot_node)
            send_data(data)
            set_sample_signal_bool = False
            # send_ok_status()

        if set_rotate_continous_signal_bool:
            final_angle = set_rotate_continous_signal_json["angle"]
            robot_node = robot.getFromDef("Robot")

            rotation_field = robot_node.getField("rotation")
            current_rotation = rotation_field.getSFRotation()
            current_angle = current_rotation[3]
            print(current_angle, current_rotation)
            if current_angle < prev_angle:
                rotations += 1
            prev_angle = current_angle

            if math.fabs(current_angle - final_angle) < 0.1:
                set_rotate_continous_signal_bool = False
                print("Rotation finished")
                front_left.setVelocity(0)
                front_right.setVelocity(0)
                send_ok_status()
            elif math.fabs(current_angle - final_angle) < 0.5:
                rotate_left()
                front_left.setVelocity(left_speed / 5)
                front_right.setVelocity(right_speed / 5)
            else:
                rotate_left()
                front_left.setVelocity(left_speed / 2)
                front_right.setVelocity(right_speed / 2)

        if set_forward_continous_signal_bool:
            final_distance = set_forward_continous_signal_json["distance"]
            robot_node = robot.getFromDef("Robot")
            position_field = robot_node.getField("translation")
            current_position = position_field.getSFVec3f()
            current_x = current_position[0]
            current_y = current_position[1]

            if init_forward == 0:
                starting_positionxy = [current_x, current_y]
                init_forward = 1
                move_forward()

            distance = math.sqrt((current_x - starting_positionxy[0]) ** 2 + (current_y - starting_positionxy[1]) ** 2)
            if distance >= final_distance:
                set_forward_continous_signal_bool = False
                print("Forward finished")
                front_left.setVelocity(0)
                front_right.setVelocity(0)
                init_forward = 0
                starting_positionxy = [0, 0]
                send_ok_status()
            elif math.fabs(distance - final_distance) < 0.2:
                front_left.setVelocity(left_speed / 5)
                front_right.setVelocity(right_speed / 5)
            else:
                front_left.setVelocity(left_speed / 2)
                front_right.setVelocity(right_speed / 2)


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

set_rotate_continous_signal_bool = False
set_rotate_continous_signal_json = {
    "angle": 0
}

set_forward_continous_signal_bool = False
set_forward_continous_signal_json = {
    "distance": 0
}


def send_ok_status():
    send_data({"status": "ok"})


def get_robot_coords():
    position = robot.getFromDef("Robot").getPosition()
    x = position[0]
    y = position[1]
    return x, y


def set_rotation_signal(angle):
    global set_rotation_signal_bool, set_rotation_signal_json
    set_rotation_signal_json["angle"] = angle
    set_rotation_signal_bool = True


def set_coords_signal(x, y):
    global set_coords_signal_bool, set_coords_signal_json
    set_coords_signal_json["x"] = x
    set_coords_signal_json["y"] = y
    set_coords_signal_bool = True


def set_robot_coords(x, y):
    robot_node = robot.getFromDef("Robot")
    translation_field = robot_node.getField("translation")
    translation_field.setSFVec3f([x, y, 0.1])
    robot.step(timestep)


def collect_current_data(robot_node):
    sensor_data = []
    for sensor in distance_sensors:
        sensor_data.append(round(sensor.getValue(), 5))

    position = robot.getFromDef("Robot").getPosition()
    x = round(position[0], 5)
    y = round(position[1], 5)

    rotation_field = robot_node.getField("rotation")
    current_rotation = rotation_field.getSFRotation()
    angle = current_rotation[3]

    data = {
        "status": "ok",
        "data": sensor_data,
        "params": {
            "x": x,
            "y": y,
            "angle": angle
        }
    }

    return data


def detach_robot_sample():
    global set_sample_signal_bool
    set_sample_signal_bool = True


def detach_robot_teleport_absolute(x: float, y: float):
    set_coords_signal(x, y)


def detach_robot_teleport_relative(dx: float, dy: float):
    x, y = get_robot_coords()
    set_coords_signal(x + dx, y + dy)


def detach_robot_rotate_absolute(angle: float):
    set_rotation_signal(angle)


def detach_robot_rotate_relative(dangle: float):
    pass


def detach_robot_rotate_continuous_absolute(angle: float):
    global set_rotate_continous_signal_bool, set_rotate_continous_signal_json
    set_rotate_continous_signal_json["angle"] = angle
    set_rotate_continous_signal_bool = True


def detach_robot_forward_continuous(distance: float):
    global set_forward_continous_signal_bool, set_forward_continous_signal_json
    set_forward_continous_signal_json["distance"] = distance
    set_forward_continous_signal_bool = True


if __name__ == '__main__':
    configs()
    config_actions(detach_robot_teleport_absolute, detach_robot_teleport_relative, detach_robot_rotate_absolute,
                   detach_robot_rotate_relative, detach_robot_sample, detach_robot_rotate_continuous_absolute,
                   detach_robot_forward_continuous)

    # external communication mechanism
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # simulation loop
    sensors_setup()
    main_loop()
