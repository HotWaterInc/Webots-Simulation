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
import numpy as np

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
    global distance_sensors

    for i in range(robot.getNumberOfDevices()):
        device = robot.getDeviceByIndex(i)
        if 'distance sensor' in device.getName():
            # Enable the distance sensor
            device.enable(timestep)
            distance_sensors.append(device)

            sensor_node = supervisor.getFromDef(device.getName())

    # invert order
    distance_sensors = distance_sensors[::-1]
    # shifts second half of sensors to the left
    half = int(len(distance_sensors) / 2)
    distance_sensors = distance_sensors[half:] + distance_sensors[:half]
    names = [sensor.getName() for sensor in distance_sensors]


def rotate_left():
    global left_speed, right_speed
    left_speed = RobotParams.get_instance().get_max_speed()
    right_speed = -RobotParams.get_instance().get_max_speed()


def rotate_right():
    global left_speed, right_speed
    left_speed = -RobotParams.get_instance().get_max_speed()
    right_speed = RobotParams.get_instance().get_max_speed()


def move_backward():
    global left_speed, right_speed
    left_speed = RobotParams.get_instance().get_max_speed()
    right_speed = RobotParams.get_instance().get_max_speed()


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
    global set_coords_signal_relative_bool, set_coords_signal_relative_json
    global set_rotation_signal_bool, set_rotation_signal_json

    global set_sample_distance_signal_bool, set_sample_image_signal_bool
    global set_rotate_continous_signal_bool, set_rotate_continous_signal_json
    global set_forward_continous_signal_bool, set_forward_continous_signal_json

    global set_W_signal_bool, set_S_signal_bool, set_A_signal_bool, set_D_signal_bool
    global init_W, init_S, init_A, init_D

    global set_robot_sample_image_inference

    starting_positionxy = [0, 0]
    starting_rotation = 0
    init_forward = 0

    rotations = 0
    prev_angle = 0

    camera = robot.getDevice("CAM_NAME")
    camera.enable(timestep)

    counter = 0

    while robot.step(timestep) != -1:
        front_left.setVelocity(0)
        front_right.setVelocity(0)

        if set_coords_signal_bool:
            x = set_coords_signal_json["x"]
            y = set_coords_signal_json["y"]
            set_robot_coords(x, y)
            set_coords_signal_bool = 0
            send_ok_status()

        if set_coords_signal_relative_bool:
            dx = set_coords_signal_relative_json["dx"]
            dy = set_coords_signal_relative_json["dy"]
            x, y = get_robot_coords()
            set_robot_coords(x + dx, y + dy)
            set_coords_signal_relative_bool = 0
            send_ok_status()

        if set_rotation_signal_bool:
            angle = set_rotation_signal_json["angle"]
            robot_node = robot.getFromDef("Robot")
            rotation_field = robot_node.getField("rotation")
            rotation_field.setSFRotation([0, 0, 1, angle])
            set_rotation_signal_bool = 0
            send_ok_status()

        if set_sample_distance_signal_bool:
            data = collect_sensor_distance_data(robot_node)
            send_data(data)
            set_sample_distance_signal_bool = 0
            # send_ok_status()

        if set_robot_sample_image_inference:
            # get pure image raw data as array
            image = camera.getImage()
            width = camera.getWidth()
            height = camera.getHeight()

            img_array = np.frombuffer(image, np.uint8).reshape((height, width, 4))
            rgb_img = img_array[:, :, :3]

            data = {
                "status": "ok",
                "data": rgb_img.tolist(),
                "params": collect_metadata(robot_node)
            }

            send_data(data)
            set_robot_sample_image_inference = 0

        if set_sample_image_signal_bool:
            # get pure image raw data as array
            image = camera.getImage()
            width = camera.getWidth()
            height = camera.getHeight()

            img_array = np.frombuffer(image, np.uint8).reshape((height, width, 4))
            rgb_img = img_array[:, :, :3]

            data = {
                "status": "ok",
                "data": rgb_img.tolist(),
                "params": collect_metadata(robot_node)
            }

            send_data(data)
            set_sample_image_signal_bool = 0

        if set_rotate_continous_signal_bool:
            final_angle = set_rotate_continous_signal_json["angle"]
            robot_node = robot.getFromDef("Robot")

            rotation_field = robot_node.getField("rotation")
            current_rotation = rotation_field.getSFRotation()
            current_angle = current_rotation[3]
            if current_angle < prev_angle:
                rotations += 1
            prev_angle = current_angle

            if math.fabs(current_angle - final_angle) < 0.1:
                set_rotate_continous_signal_bool = 0
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
                set_forward_continous_signal_bool = 0
                init_forward = 0
                # front_left.setVelocity(0)
                # front_right.setVelocity(0)
                starting_positionxy = [0, 0]
                send_ok_status()
            else:
                front_left.setVelocity(left_speed)
                front_right.setVelocity(right_speed)

        if set_W_signal_bool:
            if init_W == 1:
                init_W = 0
                set_to_0_after_delay(set_W_to_0)

            move_forward()
            send_ok_status()
            front_left.setVelocity(left_speed)
            front_right.setVelocity(right_speed)

        if set_S_signal_bool:
            if init_S == 1:
                init_S = 0
                set_to_0_after_delay(set_S_to_0)

            move_backward()
            send_ok_status()
            front_left.setVelocity(left_speed)
            front_right.setVelocity(right_speed)

        if set_A_signal_bool:
            if init_A == 1:
                init_A = 0
                set_to_0_after_delay(set_A_to_0)

            rotate_left()
            send_ok_status()
            front_left.setVelocity(left_speed)
            front_right.setVelocity(right_speed)

        if set_D_signal_bool:
            if init_D == 1:
                init_D = 0
                set_to_0_after_delay(set_D_to_0)

            rotate_right()
            send_ok_status()
            front_left.setVelocity(left_speed)
            front_right.setVelocity(right_speed)


def get_current_angle():
    global robot
    robot_node = robot.getFromDef("Robot")
    rotation_field = robot_node.getField("rotation")
    current_rotation = rotation_field.getSFRotation()

    current_angle = current_rotation[3]
    sign = current_rotation[2] < 0
    correct_angle = current_angle
    if sign == True:
        correct_angle = -current_angle

    return correct_angle


cencellation_thread = None


def set_to_0_after_delay(func):
    global cencellation_thread
    if cencellation_thread is not None:
        cencellation_thread.cancel()
    t = threading.Timer(0.1, func)
    cencellation_thread = t
    t.start()


def set_D_to_0():
    global set_D_signal_bool, init_D
    set_D_signal_bool = 0
    init_D = 0


def set_A_to_0():
    global set_A_signal_bool, init_A
    set_A_signal_bool = 0
    init_A = 0


def set_S_to_0():
    global set_S_signal_bool, init_S
    set_S_signal_bool = 0
    init_S = 0


def set_W_to_0():
    global set_W_signal_bool, init_W
    set_W_signal_bool = 0
    init_W = 0


set_save_image_signal = 0
set_robot_sample_image_inference = 0

set_coords_signal_relative_bool = 0
set_coords_signal_relative_json = {
    "dx": 0,
    "dy": 0
}

set_coords_signal_bool = 0
set_coords_signal_json = {
    "x": 0,
    "y": 0
}

set_rotation_signal_bool = 0
set_rotation_signal_json = {
    "angle": 0
}

set_sample_distance_signal_bool = 0
set_sample_image_signal_bool = 0

set_rotate_continous_signal_bool = 0
set_rotate_continous_signal_json = {
    "angle": 0
}

set_W_signal_bool = 0
set_S_signal_bool = 0
set_A_signal_bool = 0
set_D_signal_bool = 0

init_S = 0
init_A = 0
init_D = 0
init_W = 0

set_forward_continous_signal_bool = 0
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


def set_coords_signal_relative(dx, dy):
    global set_coords_signal_relative_bool, set_coords_signal_relative_json
    set_coords_signal_relative_json["dx"] = dx
    set_coords_signal_relative_json["dy"] = dy
    set_coords_signal_relative_bool = True


def set_robot_coords(x, y):
    robot_node = robot.getFromDef("Robot")
    translation_field = robot_node.getField("translation")
    translation_field.setSFVec3f([x, y, 0.1])
    robot.step(timestep)


def collect_metadata(robot_node):
    position = robot.getFromDef("Robot").getPosition()
    x = round(position[0], 5)
    y = round(position[1], 5)

    angle = get_current_angle()  # between -pi and pi

    params = {
        "x": x,
        "y": y,
        "angle": angle
    }

    return params


def collect_sensor_distance_data(robot_node):
    sensor_data = []
    for sensor in distance_sensors:
        sensor_data.append(round(sensor.getValue(), 5))

    data = {
        "status": "ok",
        "data": sensor_data,
        "params": collect_metadata(robot_node)
    }

    return data


def detach_robot_sample_distance():
    global set_sample_distance_signal_bool
    set_sample_distance_signal_bool = True


def detach_robot_sample_image():
    global set_sample_image_signal_bool
    set_sample_image_signal_bool = True


def detach_robot_teleport_absolute(x: float, y: float):
    set_coords_signal(x, y)


def detach_robot_teleport_relative(dx: float, dy: float):
    set_coords_signal_relative(dx, dy)


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


def detach_robot_W():
    global set_W_signal_bool
    global init_W
    init_W = 1
    set_W_signal_bool = 1


def detach_robot_S():
    global set_S_signal_bool, init_S
    init_S = 1
    set_S_signal_bool = 1


def detach_robot_A():
    global set_A_signal_bool
    global init_A
    init_A = 1
    set_A_signal_bool = 1


def detach_robot_D():
    global set_D_signal_bool
    global init_D
    init_D = 1
    set_D_signal_bool = 1


def detach_robot_sample_image_inference():
    global set_robot_sample_image_inference
    set_robot_sample_image_inference = 1


if __name__ == '__main__':
    configs()
    # The horrors of Webots integration
    config_actions(detach_robot_teleport_absolute, detach_robot_teleport_relative, detach_robot_rotate_absolute,
                   detach_robot_rotate_relative, detach_robot_sample_distance, detach_robot_sample_image,
                   detach_robot_sample_image_inference,
                   detach_robot_rotate_continuous_absolute,
                   detach_robot_forward_continuous, action_W=detach_robot_W, action_A=detach_robot_A,
                   action_S=detach_robot_S, action_D=detach_robot_D)

    # external communication mechanism
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # simulation loop
    sensors_setup()
    main_loop()
