# singleton instance of global params

class RobotParams:
    __instance = None
    robot = None

    @staticmethod
    def get_instance():
        if RobotParams.__instance is None:
            RobotParams()
        return RobotParams.__instance

    def __init__(self):
        if RobotParams.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            RobotParams.__instance = self
            self.robot = None
            self.timestep = None
            self.max_speed = None
            self.start_time = None
            self.distance_sensors = []

    def set_robot(self, robot):
        self.robot = robot

    def set_timestep(self, timestep):
        self.timestep = timestep

    def set_max_speed(self, max_speed):
        self.max_speed = max_speed

    def set_start_time(self, start_time):
        self.start_time = start_time

    def get_robot(self):
        return self.robot

    def get_timestep(self):
        return self.timestep

    def get_max_speed(self):
        return self.max_speed

    def get_start_time(self):
        return self.start_time

    def get_distance_sensors(self):
        return self.distance_sensors

    def add_distance_sensor(self, device):
        self.distance_sensors.append(device)
