# ignore errors in this file
from controller import Supervisor
from teleport_data_collection import Movement, TeleportType
from time import sleep as Sleep
import threading
from communication.communication_interface import send_data
from configs_init import configs, config_actions
from robot_params.robot_params import RobotParams
from robot_params.operations_interface import OperationMode, operation_mode
from communication.communication_interface import start_server

robot = Supervisor()
RobotParams.get_instance().set_robot(robot)
RobotParams.get_instance().set_timestep(64)
RobotParams.get_instance().set_max_speed(6.28)
RobotParams.get_instance().set_start_time(0.0)

start_time = robot.getTime()
distance_sensors = []

timestep = RobotParams.get_instance().get_timestep()
width = 4
height = 4
movement = Movement.get_instance()
movement.set_teleport_type(TeleportType.TELEPORT8x8, width, height)


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

    max_speed = RobotParams.get_instance().get_max_speed()
    timestep = RobotParams.get_instance().get_timestep()

    left_speed = max_speed
    right_speed = max_speed

    robot_node = robot.getFromDef("Robot")
    translation_field = robot_node.getField("translation")
    finished = 0
    offset_x = -width / 2
    offset_y = 0

    while robot.step(timestep) != -1:
        if operation_mode() == OperationMode.SEND_DATA:
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


def action1():
    print("Action 1")


def action2():
    print("Action 2")


def action3():
    print("Action 3")


if __name__ == '__main__':
    configs()
    config_actions(action1, action2, action3)

    # external communication mechanism
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    send_data("START")

    # simulation loop
    sensors_setup()
    main_loop()
